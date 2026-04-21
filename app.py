from flask import Flask, render_template, session, Blueprint, request, redirect, url_for, jsonify, flash
from flask_session import Session
from config import SECRET_KEY, SESSION_TYPE, SESSION_PERMANENT, PERMANENT_SESSION_LIFETIME
from models import Player, DecisionEngine
from services import (
    save_player_to_session,
    load_player_from_session,
    clear_session,
    has_active_game,
    get_current_decision_id,
    set_current_decision_id,
    add_decision_to_history,
    get_player_state_dict,
)
from utils import (
    validate_player_state,
    can_make_decision,
    validate_option_requirements,
    sanitize_player_state,
)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_TYPE=SESSION_TYPE,
    SESSION_PERMANENT=SESSION_PERMANENT,
    PERMANENT_SESSION_LIFETIME=PERMANENT_SESSION_LIFETIME
)

Session(app)

decision_engine = DecisionEngine()
decision_engine.load_decisions()
decision_engine.load_events()

main_bp = Blueprint('main', __name__)


def format_number(value):
    if value is None:
        return '0'
    return f"{value:,}".replace(',', '.')


def format_percentage(value, decimals=1):
    if value is None:
        return '0%'
    return f"{value:.{decimals}f}%"


def format_currency(value):
    if value is None:
        return '$0'
    return f"${value:,}".replace(',', '.')


def format_skill_bar(value, max_value=100):
    percentage = (value / max_value) * 100
    return percentage


app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['percentage'] = format_percentage
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['skill_bar'] = format_skill_bar


@main_bp.route('/')
def index():
    player = load_player_from_session()

    if player and has_active_game():
        current_decision_id = get_current_decision_id() or 'inicio'
        return redirect(url_for('main.decision_view', decision_id=current_decision_id))

    return render_template('index.html', has_active=False)


@main_bp.route('/new_game', methods=['POST'])
def new_game():
    clear_session()

    player = Player(
        nivel='trainee',
        skill_level=0,
        salario=15000,
        estres=0,
        reputacion=0,
        stack=[],
        logros=[],
        decisiones_tomadas=[],
        años_experiencia=0.0,
        nombre=request.form.get('nombre', 'Jugador')
    )

    save_player_to_session(player)
    set_current_decision_id('inicio')

    return redirect(url_for('main.decision_view', decision_id='inicio'))


@main_bp.route('/decision/<decision_id>')
def decision_view(decision_id):
    player = load_player_from_session()

    if not player:
        flash('No hay una partida activa', 'error')
        return redirect(url_for('main.index'))

    player_state = player.to_dict()

    decision = decision_engine.get_decision(decision_id, player_state)

    if not decision:
        available = decision_engine.get_all_decision_ids()
        flash(f'Decisión no disponible: {decision_id}. Disponible: {available[:5]}', 'error')
        return redirect(url_for('main.index'))

    options = decision_engine.get_available_options(decision_id, player_state)

    if not options:
        flash('No hay opciones disponibles para esta decisión', 'warning')
        return redirect(url_for('main.stats'))

    is_game_over = decision_engine.is_game_over(decision_id)
    is_victory = decision_engine.is_victory(decision_id)

    event_triggered = None
    random_event = decision_engine.trigger_random_event(player_state)
    if random_event:
        event_triggered = random_event

    if player.estres > 80 and not is_game_over:
        is_burnout_warning = True
    else:
        is_burnout_warning = False

    validation = validate_player_state(player)
    if not validation['valid']:
        for error in validation['errors']:
            flash(error, 'error')

    save_player_to_session(player)

    return render_template(
        'decision.html',
        decision=decision,
        options=options,
        player=player,
        current_decision_id=decision_id,
        is_game_over=is_game_over,
        is_victory=is_victory,
        is_burnout_warning=is_burnout_warning,
        event_triggered=event_triggered
    )


@main_bp.route('/decision/<decision_id>', methods=['POST'])
def decision_submit(decision_id):
    player = load_player_from_session()

    if not player:
        flash('No hay una partida activa', 'error')
        return redirect(url_for('main.index'))

    player_state = player.to_dict()

    option_index = request.form.get('option_index', type=int)

    decision = decision_engine.get_decision(decision_id, player_state)
    if not decision:
        flash('Decisión no encontrada', 'error')
        return redirect(url_for('main.index'))

    available_options = decision_engine.get_available_options(decision_id, player_state)

    if option_index >= len(available_options):
        flash('Opción inválida', 'error')
        return redirect(url_for('main.decision_view', decision_id=decision_id))

    selected_option = available_options[option_index]

    add_decision_to_history(decision_id, selected_option.get('label', ''))

    updated_state = decision_engine.apply_effects(decision_id, option_index, player_state)

    player_state = updated_state

    player.nivel = player_state.get('nivel', player.nivel)
    player.skill_level = player_state.get('skill_level', player.skill_level)
    player.salario = player_state.get('salario', player.salario)
    player.estres = player_state.get('estres', player.estres)
    player.reputacion = player_state.get('reputacion', player.reputacion)
    player.stack = player_state.get('stack', player.stack)
    player.logros = player_state.get('logros', player.logros)
    player.años_experiencia = player_state.get('años_experiencia', player.años_experiencia)

    result_messages = player_state.get('result_messages', [])
    if result_messages:
        for msg in result_messages:
            flash(msg, 'success')

    player.update_nivel()

    if player.estres > 80:
        save_player_to_session(player)
        set_current_decision_id('final_burnout')
        return redirect(url_for('main.decision_view', decision_id='final_burnout'))

    next_decision_id = decision_engine.get_next_decision(decision_id, option_index, player_state)

    if not next_decision_id:
        save_player_to_session(player)
        return redirect(url_for('main.stats'))

    save_player_to_session(player)
    set_current_decision_id(next_decision_id)

    if decision_engine.is_victory(next_decision_id):
        return redirect(url_for('main.decision_view', decision_id=next_decision_id))

    return redirect(url_for('main.decision_view', decision_id=next_decision_id))


@main_bp.route('/reset')
def reset():
    clear_session()
    flash('Partida reiniciada', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/stats')
def stats():
    player = load_player_from_session()

    if not player:
        return jsonify({'error': 'No hay partida activa'}), 404

    player_state = get_player_state_dict()

    validation = validate_player_state(player)
    player_state['validation'] = validation

    return jsonify(player_state)


@main_bp.route('/api/check_requirements/<decision_id>')
def check_requirements(decision_id):
    player = load_player_from_session()

    if not player:
        return jsonify({'can_make': False, 'reason': 'No hay partida activa'})

    player_state = player.to_dict()
    decision = decision_engine.get_decision(decision_id, player_state)

    if not decision:
        return jsonify({'can_make': False, 'reason': 'Decisión no encontrada'})

    requirements = decision.get('requerimientos', {})

    from utils import can_make_decision as check_can_make
    result = check_can_make(player, requirements)

    return jsonify(result)


app.register_blueprint(main_bp)


if __name__ == '__main__':
    app.run(debug=True)
