import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

VALID_LEVELS = ['trainee', 'junior', 'semi-senior', 'senior', 'lead']

STAT_RANGES = {
    'skill_level': (0, 100),
    'estres': (0, 100),
    'reputacion': (0, 100),
    'salario': (0, 50000),
    'años_experiencia': (0, 50),
}

VALID_DECISION_TYPES = [
    'inicio', 'eleccion_carrera', 'aprender', 'proyecto', 'desafio',
    'promocion', 'riesgo', 'liderazgo', 'emprendimiento',
    'evaluacion', 'reflexion', 'final', 'game_over'
]

VALID_EVENT_TYPES = ['positivo', 'negativo', 'neutral', 'riesgo']


def validate_player_state(player: Any) -> Dict[str, Any]:
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    if not hasattr(player, 'to_dict'):
        result['valid'] = False
        result['errors'].append('Player no tiene método to_dict()')
        return result

    state = player.to_dict() if hasattr(player, 'to_dict') else player

    if 'nivel' not in state:
        result['valid'] = False
        result['errors'].append('Falta atributo: nivel')
    elif state['nivel'] not in VALID_LEVELS:
        result['valid'] = False
        result['errors'].append(f'Nivel inválido: {state["nivel"]}. Debe ser uno de {VALID_LEVELS}')
        logger.warning(f'Nivel inválido detectado: {state["nivel"]}')

    for stat, (min_val, max_val) in STAT_RANGES.items():
        if stat in state:
            value = state[stat]
            if value < min_val or value > max_val:
                result['valid'] = False
                result['errors'].append(f'{stat} fuera de rango: {value} (debe estar entre {min_val} y {max_val})')
                logger.warning(f'Stats fuera de rango: {stat}={value}')

    if 'stack' in state and not isinstance(state['stack'], list):
        result['valid'] = False
        result['errors'].append('stack debe ser una lista')
        logger.warning('Stack no es una lista')

    if 'logros' in state and not isinstance(state['logros'], list):
        result['valid'] = False
        result['errors'].append('logros debe ser una lista')
        logger.warning('Logros no es una lista')

    if 'decisiones_tomadas' in state and not isinstance(state['decisiones_tomadas'], list):
        result['valid'] = False
        result['errors'].append('decisiones_tomadas debe ser una lista')
        logger.warning('Decisiones tomadas no es una lista')

    if state.get('skill_level', 0) >= 90 and state.get('nivel') != 'lead':
        result['warnings'].append(f'Skill muy alto (90+) pero nivel es {state.get("nivel")}')
        logger.debug(f'Advertencia: skill alto con nivel bajo - skill: {state.get("skill_level")}')

    if state.get('estres', 0) > 80:
        result['warnings'].append('Nivel de estrés muy alto (>80). Riesgo de burnout.')
        logger.debug(f'Advertencia burnout: estres={state.get("estres")}')

    if state.get('salario', 0) > 50000:
        result['warnings'].append('Salario máximo alcanzado')
        logger.debug('Salario máximo alcanzado')

    if len(state.get('stack', [])) > 20:
        result['warnings'].append('Stack muy grande (>20 tecnologías)')
        logger.debug(f'Stack grande: {len(state.get("stack", []))} tecnologías')

    return result


def validate_decision_transition(current_node: str, next_node: Optional[str], decisions_db: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    if next_node is None:
        result['warnings'].append('No hay siguiente nodo definido')
        return result

    if not next_node and current_node != 'final_victory' and current_node != 'final_burnout':
        result['valid'] = False
        result['errors'].append(f'Nodo terminal sin transición final: {current_node}')
        logger.warning(f'Transición sin destino: {current_node} -> None')
        return result

    if next_node not in decisions_db and next_node:
        result['valid'] = False
        result['errors'].append(f'Nodo destino no existe: {next_node}')
        logger.warning(f'Nodo inexistente: {next_node}')
        return result

    if current_node == 'inicio' and next_node not in ['primera_entrevista']:
        if next_node and next_node != 'inicio':
            result['warnings'].append(f'Desde inicio ir a {next_node} es inusual')

    if current_node == 'final_victory' and next_node:
        result['valid'] = False
        result['errors'].append('No puede haber transición después de victory')
        logger.warning(f'Transición después de victory: {current_node} -> {next_node}')

    if current_node == 'final_burnout' and next_node and next_node != 'inicio':
        result['valid'] = False
        result['errors'].append('Desde burnout solo se puede reiniciar (ir a inicio)')
        logger.warning(f'Transición inválida desde burnout: {current_node} -> {next_node}')

    return result


def can_make_decision(player: Any, decision_requirements: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    result = {
        'can_make': True,
        'reasons': [],
    }

    if decision_requirements is None:
        return result

    state = player.to_dict() if hasattr(player, 'to_dict') else player

    skill_min = decision_requirements.get('skill_min')
    if skill_min is not None:
        current_skill = state.get('skill_level', 0)
        if current_skill < skill_min:
            result['can_make'] = False
            result['reasons'].append(f'Skill mínimo requerido: {skill_min}, actual: {current_skill}')
            logger.debug(f'Rechazado por skill: {current_skill} < {skill_min}')

    reputacion_min = decision_requirements.get('reputacion_min')
    if reputacion_min is not None:
        current_reputacion = state.get('reputacion', 0)
        if current_reputacion < reputacion_min:
            result['can_make'] = False
            result['reasons'].append(f'Reputación mínima requerida: {reputacion_min}, actual: {current_reputacion}')
            logger.debug(f'Rechazado por reputación: {current_reputacion} < {reputacion_min}')

    años_min = decision_requirements.get('años_experiencia_min')
    if años_min is not None:
        current_años = state.get('años_experiencia', 0)
        if current_años < años_min:
            result['can_make'] = False
            result['reasons'].append(f'Años de experiencia mínimos: {años_min}, actual: {current_años:.1f}')
            logger.debug(f'Rechazado por experiencia: {current_años} < {años_min}')

    nivel_required = decision_requirements.get('nivel')
    if nivel_required is not None:
        current_nivel = state.get('nivel', 'trainee')
        if current_nivel != nivel_required:
            result['can_make'] = False
            result['reasons'].append(f'Nivel requerido: {nivel_required}, actual: {current_nivel}')
            logger.debug(f'Rechazado por nivel: {current_nivel} != {nivel_required}')

    stack_required = decision_requirements.get('stack')
    if stack_required is not None:
        player_stack = state.get('stack', [])
        if stack_required not in player_stack:
            result['can_make'] = False
            result['reasons'].append(f'Stack requerido: {stack_required}, stack actual: {player_stack}')
            logger.debug(f'Rechazado por stack: {stack_required} no está en {player_stack}')

    stack_min = decision_requirements.get('stack_min')
    if stack_min is not None:
        player_stack = state.get('stack', [])
        if len(player_stack) < stack_min:
            result['can_make'] = False
            result['reasons'].append(f'Stack mínimo: {stack_required} tecnologías, actual: {len(player_stack)}')
            logger.debug(f'Rechazado por stack_min: {len(player_stack)} < {stack_min}')

    flag_required = decision_requirements.get('flag')
    if flag_required is not None:
        flags = state.get('flags', {})
        if not flags.get(flag_required, False):
            result['can_make'] = False
            result['reasons'].append(f'Flag requerida: {flag_required}')
            logger.debug(f'Rechazado por flag: {flag_required} no está activa')

    return result


def validate_option_requirements(player: Any, option: Dict[str, Any]) -> bool:
    req = option.get('requiere')
    if req is None:
        return True

    result = can_make_decision(player, req)
    return result['can_make']


def validate_decision_node(decision: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    required_fields = ['id', 'titulo', 'descripcion', 'opciones']
    for field in required_fields:
        if field not in decision:
            result['valid'] = False
            result['errors'].append(f'Campo requerido faltante: {field}')

    if 'tipo' in decision:
        if decision['tipo'] not in VALID_DECISION_TYPES:
            result['warnings'].append(f'Tipo de decisión desconocido: {decision["tipo"]}')
            logger.debug(f'Tipo desconocido: {decision["tipo"]}')

    opciones = decision.get('opciones', [])
    if not opciones:
        result['warnings'].append('Decisión sin opciones')
    else:
        for i, option in enumerate(opciones):
            if 'label' not in option:
                result['errors'].append(f'Opción {i} sin label')
            if 'next_node' not in option:
                result['warnings'].append(f'Opción {i} sin next_node')

    return result


def validate_event(event: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    required_fields = ['id', 'titulo', 'descripcion', 'tipo', 'probabilidad', 'efectos']
    for field in required_fields:
        if field not in event:
            result['valid'] = False
            result['errors'].append(f'Campo requerido faltante: {field}')

    if 'tipo' in event:
        if event['tipo'] not in VALID_EVENT_TYPES:
            result['warnings'].append(f'Tipo de evento desconocido: {event["tipo"]}')

    prob = event.get('probabilidad')
    if prob is not None:
        if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
            result['valid'] = False
            result['errors'].append(f'Probabilidad inválida: {prob} (debe estar entre 0 y 1)')
            logger.warning(f'Probabilidad inválida en evento {event.get("id")}: {prob}')

    return result


def sanitize_player_state(state: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = state.copy()

    if 'nivel' in sanitized and sanitized['nivel'] not in VALID_LEVELS:
        logger.warning(f'Sanitizando nivel: {sanitized["nivel"]} -> trainee')
        sanitized['nivel'] = 'trainee'

    for stat, (min_val, max_val) in STAT_RANGES.items():
        if stat in sanitized:
            value = sanitized[stat]
            if not isinstance(value, (int, float)):
                sanitized[stat] = min_val
                logger.warning(f'Sanitizando {stat}: valor no numérico -> {min_val}')
            elif value < min_val:
                sanitized[stat] = min_val
                logger.warning(f'Sanitizando {stat}: {value} < {min_val} -> {min_val}')
            elif value > max_val:
                sanitized[stat] = max_val
                logger.warning(f'Sanitizando {stat}: {value} > {max_val} -> {max_val}')

    if 'stack' not in sanitized or not isinstance(sanitized['stack'], list):
        sanitized['stack'] = []
    else:
        sanitized['stack'] = list(set(sanitized['stack']))

    if 'logros' not in sanitized or not isinstance(sanitized['logros'], list):
        sanitized['logros'] = []
    else:
        sanitized['logros'] = list(set(sanitized['logros']))

    if 'flags' not in sanitized or not isinstance(sanitized['flags'], dict):
        sanitized['flags'] = {}

    return sanitized
