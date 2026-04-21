from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class EffectResult:
    success: bool
    message: str
    stat_changed: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


STAT_RANGES = {
    'skill_level': (0, 100),
    'estres': (0, 100),
    'reputacion': (0, 100),
    'salario': (0, 50000),
    'años_experiencia': (0, 50),
}

NUMERIC_STATS = {'skill_level', 'estres', 'reputacion', 'salario', 'años_experiencia'}


def _validate_and_clamp(stat: str, value: float) -> float:
    if stat in STAT_RANGES:
        min_val, max_val = STAT_RANGES[stat]
        return max(min_val, min(max_val, value))
    return value


def _format_message(effect_type: str, label: str, old_val: Any, new_val: Any, stat: str = '') -> str:
    if effect_type == 'stat_change':
        sign = '+' if new_val > old_val else ''
        if stat == 'salario':
            return f"Salario {sign}${new_val:,.0f}" if new_val > old_val else f"Salario: ${new_val:,.0f}"
        elif stat in ['skill_level', 'estres', 'reputacion']:
            return f"{label}: {sign}{new_val - old_val:+.0f} ({new_val:.0f})"
        return f"{label}: {sign}{new_val - old_val:+.1f}"
    elif effect_type == 'add_tech':
        return f"Nueva tecnología: {new_val}"
    elif effect_type == 'remove_tech':
        return f"Tecnología eliminada: {new_val}"
    elif effect_type == 'add_achievement':
        return f"🏆 Logro: {new_val}"
    elif effect_type == 'set_flag':
        return f"Bandera activada: {label}"
    elif effect_type == 'trigger_event':
        return f"⚡ Evento: {label}"
    elif effect_type == 'level_change':
        return f"🎉 Nivel: {new_val}"
    return f"{label}: {new_val}"


def apply_stat_change(
    player_state: Dict[str, Any],
    stat: str,
    delta: float
) -> EffectResult:
    if stat not in player_state:
        return EffectResult(False, f"Stat '{stat}' no existe", None, None, None)

    old_value = player_state[stat]
    new_value = _validate_and_clamp(stat, old_value + delta)
    player_state[stat] = new_value

    label = stat.replace('_', ' ').title()
    message = _format_message('stat_change', label, old_value, new_value, stat)

    return EffectResult(True, message, stat, old_value, new_value)


def apply_stat_set(
    player_state: Dict[str, Any],
    stat: str,
    value: float
) -> EffectResult:
    if stat not in player_state:
        return EffectResult(False, f"Stat '{stat}' no existe", None, None, None)

    old_value = player_state[stat]
    new_value = _validate_and_clamp(stat, value)
    player_state[stat] = new_value

    label = stat.replace('_', ' ').title()
    message = f"{label}: {new_value}"

    return EffectResult(True, message, stat, old_value, new_value)


def apply_add_tech(
    player_state: Dict[str, Any],
    tech: str
) -> EffectResult:
    if 'stack' not in player_state:
        player_state['stack'] = []

    stack = player_state['stack']
    if tech in stack:
        return EffectResult(False, f"'{tech}' ya está en tu stack", 'stack', tech, tech)

    stack.append(tech)
    message = _format_message('add_tech', '', None, tech)

    return EffectResult(True, message, 'stack', None, tech)


def apply_remove_tech(
    player_state: Dict[str, Any],
    tech: str
) -> EffectResult:
    if 'stack' not in player_state:
        return EffectResult(False, "Stack vacío", 'stack', None, None)

    stack = player_state['stack']
    if tech not in stack:
        return EffectResult(False, f"'{tech}' no está en tu stack", 'stack', None, None)

    stack.remove(tech)
    message = _format_message('remove_tech', '', None, tech)

    return EffectResult(True, message, 'stack', tech, None)


def apply_add_achievement(
    player_state: Dict[str, Any],
    achievement: str
) -> EffectResult:
    if 'logros' not in player_state:
        player_state['logros'] = []

    logros = player_state['logros']
    if achievement in logros:
        return EffectResult(False, f"'{achievement}' ya logrado", 'logros', achievement, achievement)

    logros.append(achievement)
    message = _format_message('add_achievement', '', None, achievement)

    return EffectResult(True, message, 'logros', None, achievement)


def apply_set_flag(
    player_state: Dict[str, Any],
    flag_name: str,
    value: bool = True
) -> EffectResult:
    if 'flags' not in player_state:
        player_state['flags'] = {}

    old_value = player_state['flags'].get(flag_name, False)
    player_state['flags'][flag_name] = value
    message = _format_message('set_flag', flag_name.replace('_', ' ').title(), old_value, value)

    return EffectResult(True, message, 'flags', old_value, value)


def apply_trigger_event(
    player_state: Dict[str, Any],
    event_name: str
) -> EffectResult:
    if 'active_events' not in player_state:
        player_state['active_events'] = []

    active = player_state['active_events']
    if event_name in active:
        return EffectResult(False, f"Evento '{event_name}' ya activo", 'active_events', None, None)

    active.append(event_name)
    message = _format_message('trigger_event', '', None, event_name)

    return EffectResult(True, message, 'active_events', None, event_name)


def apply_level_change(
    player_state: Dict[str, Any],
    new_level: str
) -> EffectResult:
    from models.player import BASE_SALARIES

    old_level = player_state.get('nivel', 'trainee')
    old_salary = player_state.get('salario', 0)

    player_state['nivel'] = new_level
    new_salary = BASE_SALARIES.get(new_level, old_salary)
    player_state['salario'] = new_salary

    message = f"🎉 Nivel: {old_level} → {new_level} (Salario: ${new_salary:,})"

    return EffectResult(True, message, 'nivel', old_level, new_level)


def apply_conditional_effect(
    player_state: Dict[str, Any],
    condition_stat: str,
    condition_operator: str,
    condition_value: float,
    then_effects: List[Dict[str, Any]]
) -> EffectResult:
    if condition_stat not in player_state:
        return EffectResult(False, f"Condition stat '{condition_stat}' no existe", None, None, None)

    current_value = player_state[condition_stat]
    condition_met = _evaluate_condition(current_value, condition_operator, condition_value)

    if not condition_met:
        return EffectResult(False, "Condición no cumplida", condition_stat, current_value, current_value)

    result = apply_effects_batch(player_state, then_effects)
    if result:
        return EffectResult(True, f"Condición cumplida: {condition_stat} {condition_operator} {condition_value}. " + result[0].message, condition_stat, current_value, current_value)

    return EffectResult(True, f"Condición cumplida, sin efectos adicionales", condition_stat, current_value, current_value)


def _evaluate_condition(value: float, operator: str, target: float) -> bool:
    operators = {
        '>': lambda v, t: v > t,
        '>=': lambda v, t: v >= t,
        '<': lambda v, t: v < t,
        '<=': lambda v, t: v <= t,
        '==': lambda v, t: v == t,
        '!=': lambda v, t: v != t,
    }
    return operators.get(operator, lambda v, t: False)(value, target)


def apply_effects_batch(
    player_state: Dict[str, Any],
    effects: List[Dict[str, Any]]
) -> List[EffectResult]:
    results: List[EffectResult] = []

    for effect in effects:
        effect_type = effect.get('type')
        result = _dispatch_effect(player_state, effect, effect_type)
        if result:
            results.append(result)

    return results


def _dispatch_effect(
    player_state: Dict[str, Any],
    effect: Dict[str, Any],
    effect_type: str
) -> Optional[EffectResult]:
    handlers = {
        'stat_change': _handle_stat_change,
        'add_tech': _handle_add_tech,
        'remove_tech': _handle_remove_tech,
        'add_achievement': _handle_add_achievement,
        'trigger_event': _handle_trigger_event,
        'set_flag': _handle_set_flag,
        'conditional_effect': _handle_conditional_effect,
        'level_change': _handle_level_change,
    }

    handler = handlers.get(effect_type)
    if not handler:
        return EffectResult(False, f"Tipo de efecto desconocido: {effect_type}", None, None, None)

    return handler(player_state, effect)


def _handle_stat_change(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    stat = effect.get('stat')
    delta = effect.get('delta')
    set_val = effect.get('set')

    if delta is not None:
        return apply_stat_change(player_state, stat, delta)
    elif set_val is not None:
        return apply_stat_set(player_state, stat, set_val)

    return EffectResult(False, f" stat_change sin delta ni set", None, None, None)


def _handle_add_tech(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    tech = effect.get('add')
    if not tech:
        return EffectResult(False, " add sin tecnología", None, None, None)
    return apply_add_tech(player_state, tech)


def _handle_remove_tech(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    tech = effect.get('remove')
    if not tech:
        return EffectResult(False, " remove sin tecnología", None, None, None)
    return apply_remove_tech(player_state, tech)


def _handle_add_achievement(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    logro = effect.get('logro')
    if not logro:
        return EffectResult(False, " add_achievement sin logro", None, None, None)
    return apply_add_achievement(player_state, logro)


def _handle_trigger_event(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    event_name = effect.get('trigger_event')
    if not event_name:
        return EffectResult(False, " trigger_event sin nombre", None, None, None)
    return apply_trigger_event(player_state, event_name)


def _handle_set_flag(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    flag_name = effect.get('flag')
    value = effect.get('value', True)
    if not flag_name:
        return EffectResult(False, " set_flag sin nombre", None, None, None)
    return apply_set_flag(player_state, flag_name, value)


def _handle_conditional_effect(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    condition_stat = effect.get('condition_stat')
    condition_operator = effect.get('condition_operator', '>=')
    condition_value = effect.get('condition_value')
    then_effects = effect.get('then_effects', [])

    if not condition_stat or condition_value is None:
        return EffectResult(False, " conditional_effect incompleto", None, None, None)

    return apply_conditional_effect(
        player_state,
        condition_stat,
        condition_operator,
        condition_value,
        then_effects
    )


def _handle_level_change(
    player_state: Dict[str, Any],
    effect: Dict[str, Any]
) -> Optional[EffectResult]:
    new_level = effect.get('set')
    if not new_level:
        return EffectResult(False, " level_change sin nivel", None, None, None)
    return apply_level_change(player_state, new_level)


def get_player_summary(player_state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'nivel': player_state.get('nivel', 'trainee'),
        'skill_level': player_state.get('skill_level', 0),
        'salario': player_state.get('salario', 15000),
        'estres': player_state.get('estres', 0),
        'reputacion': player_state.get('reputacion', 0),
        'años_experiencia': player_state.get('años_experiencia', 0),
        'stack_count': len(player_state.get('stack', [])),
        'logros_count': len(player_state.get('logros', [])),
        'is_burned_out': player_state.get('estres', 0) > 80,
    }