import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from models import Player


SAVES_DIR = 'saves'


def ensure_saves_dir() -> Path:
    path = Path(SAVES_DIR)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def export_player_state(player: Player, include_history: bool = True) -> Dict[str, Any]:
    state = player.to_dict()

    export_data = {
        'version': 2,
        'exported_at': datetime.now().isoformat(),
        'player': state,
        'game_stats': {
            'total_skill_gained': state.get('skill_level', 0),
            'total_salary_earned': _calculate_total_earnings(state),
            'decisions_made': len(state.get('decisiones_tomadas', [])),
            'technologies_learned': len(state.get('stack', [])),
            'achievements_unlocked': len(state.get('logros', []))
        }
    }

    return export_data


def _calculate_total_earnings(state: Dict[str, Any]) -> int:
    decisiones = state.get('decisiones_tomadas', [])
    base_salary = 15000
    total = 0

    for decision in decisiones:
        total += base_salary

    total += state.get('salario', 0) * state.get('años_experiencia', 0)

    return int(total)


def export_to_file(player: Player, filename: Optional[str] = None, include_history: bool = True) -> Dict[str, Any]:
    ensure_saves_dir()

    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        player_name = player.nombre or 'player'
        safe_name = ''.join(c for c in player_name if c.isalnum())
        filename = f'{safe_name}_{timestamp}.json'

    if not filename.endswith('.json'):
        filename += '.json'

    export_data = export_player_state(player, include_history)

    filepath = Path(SAVES_DIR) / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return {
        'success': True,
        'filename': filename,
        'filepath': str(filepath),
        'exported_at': export_data['exported_at'],
        'player_name': player.nombre,
        'level': player.nivel,
        'skill': player.skill_level
    }


def import_from_file(filename: str) -> Optional[Player]:
    filepath = Path(SAVES_DIR) / filename

    if not filepath.exists():
        filepath = Path(filename)
        if not filepath.exists():
            return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            export_data = json.load(f)

        return _player_from_export(export_data)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f'Error importing save file: {e}')
        return None


def _player_from_export(export_data: Dict[str, Any]) -> Optional[Player]:
    player_data = export_data.get('player', {})

    if not player_data:
        return None

    try:
        player = Player(
            nivel=player_data.get('nivel', 'trainee'),
            skill_level=player_data.get('skill_level', 0),
            salario=player_data.get('salario', 15000),
            estres=player_data.get('estres', 0),
            reputacion=player_data.get('reputacion', 0),
            stack=player_data.get('stack', []),
            logros=player_data.get('logros', []),
            decisiones_tomadas=player_data.get('decisiones_tomadas', []),
            años_experiencia=player_data.get('años_experiencia', 0.0),
            nombre=player_data.get('nombre', '')
        )
        return player

    except (TypeError, KeyError) as e:
        print(f'Error creating player from export: {e}')
        return None


def list_saves() -> List[Dict[str, Any]]:
    ensure_saves_dir()

    saves = []
    saves_dir = Path(SAVES_DIR)

    for filepath in saves_dir.glob('*.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            saves.append({
                'filename': filepath.name,
                'imported_at': datetime.fromisoformat(data['exported_at']).strftime('%Y-%m-%d %H:%M'),
                'player_name': data.get('player', {}).get('nombre', 'Unknown'),
                'level': data.get('player', {}).get('nivel', 'N/A'),
                'skill': data.get('player', {}).get('skill_level', 0),
                'salary': data.get('player', {}).get('salario', 0),
                'filepath': str(filepath)
            })

        except (json.JSONDecodeError, KeyError):
            continue

    saves.sort(key=lambda x: x['imported_at'], reverse=True)
    return saves


def delete_save(filename: str) -> bool:
    filepath = Path(SAVES_DIR) / filename

    if not filepath.exists():
        return False

    try:
        filepath.unlink()
        return True
    except OSError:
        return False


def export_career_summary(player: Player) -> Dict[str, Any]:
    state = player.to_dict()

    from utils.career_paths import (
        get_career_trajectory,
        calculate_salary_multiplier,
        get_next_milestone,
        generate_career_advice,
        calculate_career_score
    )

    career_score = calculate_career_score(state)
    trajectory = get_career_trajectory(state)
    salary_mult = calculate_salary_multiplier(state)
    next_milestone = get_next_milestone(state)
    advice = generate_career_advice(state)

    return {
        'player_name': player.nombre,
        'generated_at': datetime.now().isoformat(),
        'career_summary': {
            'trajectory': trajectory,
            'career_score': career_score,
            'salary_multiplier': salary_mult,
            'next_milestone': {
                'name': next_milestone.name if next_milestone else None,
                'skill_required': next_milestone.skill_required if next_milestone else None,
                'description': next_milestone.description if next_milestone else None
            } if next_milestone else None,
            'advice_count': len(advice),
            'top_advice': [
                {'title': a.title, 'description': a.description}
                for a in advice[:3]
            ]
        },
        'player_stats': {
            'level': player.nivel,
            'skill': player.skill_level,
            'salary': player.salario,
            'stress': player.estres,
            'reputation': player.reputacion,
            'experience_years': player.años_experiencia,
            'technologies': player.stack,
            'achievements': player.logros,
            'decisions_made': len(player.decisiones_tomadas)
        }
    }


def generate_shareable_link(player: Player) -> str:
    state = player.to_dict()

    minimal_state = {
        'n': player.nombre,
        'l': player.nivel,
        's': player.skill_level,
        'sa': player.salario,
        'e': player.estres,
        'r': player.reputacion,
        'x': player.años_experiencia,
        'st': player.stack[:5],
        'lo': player.logros
    }

    encoded = json.dumps(minimal_state, separators=(',', ':'))
    import base64
    b64 = base64.b64encode(encoded.encode()).decode()

    return f"/import?data={b64}"


def import_from_shareable_link(data: str) -> Optional[Player]:
    try:
        import base64
        decoded = base64.b64decode(data.encode()).decode()
        minimal_state = json.loads(decoded)

        player = Player(
            nombre=minimal_state.get('n', 'Player'),
            nivel=minimal_state.get('l', 'trainee'),
            skill_level=minimal_state.get('s', 0),
            salario=minimal_state.get('sa', 15000),
            estres=minimal_state.get('e', 0),
            reputacion=minimal_state.get('r', 0),
            stack=minimal_state.get('st', []),
            logros=minimal_state.get('lo', []),
            decisiones_tomadas=[],
            años_experiencia=minimal_state.get('x', 0.0)
        )
        return player

    except (json.JSONDecodeError, KeyError, base64.binascii.Error):
        return None


if __name__ == '__main__':
    print("=== Simulador IT - Export/Import ===")
    print("\nFunciones disponibles:")
    print("  - export_to_file(player, filename)")
    print("  - import_from_file(filename)")
    print("  - list_saves()")
    print("  - delete_save(filename)")
    print("  - export_career_summary(player)")
    print("  - generate_shareable_link(player)")
    print("  - import_from_shareable_link(data)")
    print(f"\nDirectorio de saves: {SAVES_DIR}")
