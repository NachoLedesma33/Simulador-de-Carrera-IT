from flask import Flask, render_template, session, Blueprint
from flask_session import Session
from config import SECRET_KEY, SESSION_TYPE, SESSION_PERMANENT, PERMANENT_SESSION_LIFETIME
from models import Player

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_TYPE=SESSION_TYPE,
    SESSION_PERMANENT=SESSION_PERMANENT,
    PERMANENT_SESSION_LIFETIME=PERMANENT_SESSION_LIFETIME
)

Session(app)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


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

app.register_blueprint(main_bp)


def get_player() -> Player:
    if 'player' not in session:
        session['player'] = Player()
    return session['player']


def save_player(player: Player):
    session['player'] = player


if __name__ == '__main__':
    app.run(debug=True)
