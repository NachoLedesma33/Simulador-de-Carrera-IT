import json
from typing import Dict, Any, Optional
from flask import session
from models import Player


SESSION_KEY = 'player_data'
SESSION_VERSION = 2


def _get_player_data() -> Dict[str, Any]:
    return session.get(SESSION_KEY, {})


def _set_player_data(data: Dict[str, Any]):
    session[SESSION_KEY] = data


def save_player_to_session(player: Player) -> bool:
    try:
        player_dict = player.to_dict()
        player_dict['_version'] = SESSION_VERSION

        _set_player_data(player_dict)
        return True
    except Exception:
        return False


def load_player_from_session() -> Optional[Player]:
    data = _get_player_data()

    if not data:
        return None

    data = migrate_session(data)

    try:
        player = Player(
            nivel=data.get('nivel', 'trainee'),
            skill_level=data.get('skill_level', 0),
            salario=data.get('salario', 15000),
            estres=data.get('estres', 0),
            reputacion=data.get('reputacion', 0),
            stack=data.get('stack', []),
            logros=data.get('logros', []),
            decisiones_tomadas=data.get('decisiones_tomadas', []),
            años_experiencia=data.get('años_experiencia', 0.0),
            nombre=data.get('nombre', ''),
        )
        return player
    except Exception:
        return None


def clear_session():
    if SESSION_KEY in session:
        del session[SESSION_KEY]


def update_player_in_session(updates: Dict[str, Any]) -> bool:
    data = _get_player_data()

    if not data:
        return False

    data = migrate_session(data)

    valid_fields = {
        'nivel', 'skill_level', 'salario', 'estres', 'reputacion',
        'stack', 'logros', 'decisiones_tomadas', 'años_experiencia', 'nombre'
    }

    for key, value in updates.items():
        if key in valid_fields:
            data[key] = value

    data['_version'] = SESSION_VERSION

    _set_player_data(data)
    return True


def has_active_game() -> bool:
    data = _get_player_data()

    if not data:
        return False

    data = migrate_session(data)

    has_progress = (
        data.get('skill_level', 0) > 0 or
        data.get('años_experiencia', 0) > 0 or
        len(data.get('stack', [])) > 0 or
        len(data.get('logros', [])) > 0 or
        len(data.get('decisiones_tomadas', [])) > 0
    )

    return has_progress


def get_current_decision_id() -> Optional[str]:
    data = _get_player_data()
    return data.get('_current_decision')


def set_current_decision_id(decision_id: str):
    data = _get_player_data()
    data['_current_decision'] = decision_id
    _set_player_data(data)


def migrate_session(data: Dict[str, Any]) -> Dict[str, Any]:
    current_version = data.get('_version', 1)

    if current_version == SESSION_VERSION:
        return data

    if current_version < 2:
        if 'nivel' in data and 'nivel' not in ['trainee', 'junior', 'semi-senior', 'senior', 'lead']:
            data['nivel'] = 'trainee'

        if 'stack' not in data:
            data['stack'] = []
        if 'logros' not in data:
            data['logros'] = []
        if 'decisiones_tomadas' not in data:
            data['decisiones_tomadas'] = []

        if 'flags' not in data:
            data['flags'] = {}

    data['_version'] = SESSION_VERSION
    return data


def reset_player_state():
    clear_session()


def get_player_state_dict() -> Optional[Dict[str, Any]]:
    data = _get_player_data()
    if not data:
        return None
    return migrate_session(data)


def add_decision_to_history(decision_id: str, option_label: str):
    data = _get_player_data()
    data = migrate_session(data)

    if 'decisiones_tomadas' not in data:
        data['decisiones_tomadas'] = []

    data['decisiones_tomadas'].append({
        'decision_id': decision_id,
        'option_label': option_label,
    })

    _set_player_data(data)


def set_flag(flag_name: str, value: bool = True):
    data = _get_player_data()
    data = migrate_session(data)

    if 'flags' not in data:
        data['flags'] = {}

    data['flags'][flag_name] = value
    _set_player_data(data)


def get_flag(flag_name: str) -> bool:
    data = _get_player_data()
    data = migrate_session(data)

    return data.get('flags', {}).get(flag_name, False)
