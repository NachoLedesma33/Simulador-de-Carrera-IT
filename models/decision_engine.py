import yaml
import random
from typing import Dict, List, Any, Optional
from pathlib import Path


class DecisionEngine:
    def __init__(self):
        self.decisions: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.current_decision_id: Optional[str] = None

    def load_decisions(self, filepath: str = 'data/decisions.yaml'):
        path = Path(filepath)
        if not path.exists():
            path = Path(__file__).parent.parent / filepath

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.decisions = data

    def load_events(self, filepath: str = 'data/events.yaml'):
        path = Path(filepath)
        if not path.exists():
            path = Path(__file__).parent.parent / filepath

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            events_data = data.get('eventos_aleatorios', [])
            self.events = list(events_data.values()) if isinstance(events_data, dict) else events_data

    def get_decision(self, decision_id: str, player_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        decision = self.decisions.get(decision_id)
        if not decision:
            return None

        if self._check_requirements(decision.get('requerimientos', {}), player_state):
            return decision
        return None

    def _check_requirements(self, requirements: Dict[str, Any], player_state: Dict[str, Any]) -> bool:
        if not requirements:
            return True

        skill_min = requirements.get('skill_min')
        if skill_min is not None and player_state.get('skill_level', 0) < skill_min:
            return False

        reputacion_min = requirements.get('reputacion_min')
        if reputacion_min is not None and player_state.get('reputacion', 0) < reputacion_min:
            return False

        años_min = requirements.get('años_experiencia_min')
        if años_min is not None and player_state.get('años_experiencia', 0) < años_min:
            return False

        nivel = requirements.get('nivel')
        if nivel and player_state.get('nivel') != nivel:
            return False

        stack_required = requirements.get('stack')
        if stack_required:
            player_stack = player_state.get('stack', [])
            if stack_required not in player_stack:
                return False

        stack_min = requirements.get('stack_min')
        if stack_min is not None:
            player_stack = player_state.get('stack', [])
            if len(player_stack) < stack_min:
                return False

        return True

    def get_available_options(self, decision_id: str, player_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        decision = self.get_decision(decision_id, player_state)
        if not decision:
            return []

        options = decision.get('opciones', [])
        available = []

        for option in options:
            req = option.get('requiere')
            if self._check_requirements(req, player_state):
                available.append(option)

        return available

    def apply_effects(self, decision_id: str, option_index: int, player_state: Dict[str, Any]) -> Dict[str, Any]:
        decision = self.get_decision(decision_id, player_state)
        if not decision:
            return player_state

        options = decision.get('opciones', [])
        if option_index >= len(options):
            return player_state

        option = options[option_index]
        efectos = option.get('efectos', [])

        result_messages = []

        for efecto in efectos:
            stat = efecto.get('stat')
            delta = efecto.get('delta')
            set_value = efecto.get('set')
            add_item = efecto.get('add')
            logro = efecto.get('logro')
            trigger_event = efecto.get('trigger_event')

            if stat in player_state:
                if delta is not None:
                    current = player_state.get(stat, 0)
                    if stat == 'salario':
                        player_state[stat] = max(0, min(50000, current + delta))
                    elif stat == 'skill_level':
                        player_state[stat] = max(0, min(100, current + delta))
                    elif stat == 'estres':
                        player_state[stat] = max(0, min(100, current + delta))
                    elif stat == 'reputacion':
                        player_state[stat] = max(0, min(100, current + delta))
                    elif stat == 'años_experiencia':
                        player_state[stat] = current + delta
                    else:
                        player_state[stat] = current + delta

                elif set_value is not None:
                    player_state[stat] = set_value

            if add_item:
                if 'stack' not in player_state:
                    player_state['stack'] = []
                if add_item not in player_state['stack']:
                    player_state['stack'].append(add_item)

            if logro:
                if 'logros' not in player_state:
                    player_state['logros'] = []
                if logro not in player_state['logros']:
                    player_state['logros'].append(logro)
                    result_messages.append(f"¡Nuevo logro desbloqueado: {logro}!")

            if trigger_event:
                result_messages.append(f"Evento especial activado: {trigger_event}")

        mensaje_extra = option.get('mensaje_extra')
        if mensaje_extra:
            result_messages.insert(0, mensaje_extra)

        player_state['result_messages'] = result_messages
        return player_state

    def get_next_decision(self, decision_id: str, option_index: int, player_state: Dict[str, Any]) -> Optional[str]:
        decision = self.get_decision(decision_id, player_state)
        if not decision:
            return None

        options = decision.get('opciones', [])
        if option_index >= len(options):
            return None

        next_node = options[option_index].get('next_node')
        return next_node

    def check_burnout(self, player_state: Dict[str, Any]) -> bool:
        return player_state.get('estres', 0) > 80

    def get_burnout_decision(self) -> Optional[Dict[str, Any]]:
        return self.decisions.get('final_burnout')

    def trigger_random_event(self, player_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        available_events = []

        for event in self.events:
            if self._check_requirements(event.get('requerimientos', {}), player_state):
                if random.random() < event.get('probabilidad', 0.1):
                    available_events.append(event)

        if not available_events:
            return None

        event = random.choice(available_events)
        self._apply_event_effects(event, player_state)
        return event

    def _apply_event_effects(self, event: Dict[str, Any], player_state: Dict[str, Any]):
        efectos = event.get('efectos', [])
        for efecto in efectos:
            stat = efecto.get('stat')
            delta = efecto.get('delta')
            set_value = efecto.get('set')
            add_item = efecto.get('add')
            logro = efecto.get('logro')

            if stat in player_state:
                if delta is not None:
                    current = player_state.get(stat, 0)
                    if stat in ['salario', 'skill_level', 'estres', 'reputacion']:
                        player_state[stat] = max(0, min(100 if stat != 'salario' else 50000, current + delta))
                    else:
                        player_state[stat] = current + delta

                elif set_value is not None:
                    player_state[stat] = set_value

            if add_item:
                if 'stack' not in player_state:
                    player_state['stack'] = []
                if add_item not in player_state['stack']:
                    player_state['stack'].append(add_item)

            if logro:
                if 'logros' not in player_state:
                    player_state['logros'] = []
                if logro not in player_state['logros']:
                    player_state['logros'].append(logro)

    def is_final_decision(self, decision_id: str) -> bool:
        decision = self.decisions.get(decision_id, {})
        return decision.get('tipo') in ['final', 'game_over']

    def is_victory(self, decision_id: str) -> bool:
        return decision_id == 'final_victory'

    def is_game_over(self, decision_id: str) -> bool:
        return decision_id == 'final_burnout'

    def get_all_decision_ids(self) -> List[str]:
        return list(self.decisions.keys())

    def get_decision_type(self, decision_id: str) -> str:
        decision = self.decisions.get(decision_id, {})
        return decision.get('tipo', 'unknown')

    def get_starting_decision(self) -> str:
        return 'inicio'

    def get_decision_options_labels(self, decision_id: str, player_state: Dict[str, Any]) -> List[str]:
        options = self.get_available_options(decision_id, player_state)
        return [opt.get('label', '') for opt in options]

    def can_progress(self, player_state: Dict[str, Any]) -> bool:
        if self.check_burnout(player_state):
            return False

        skill = player_state.get('skill_level', 0)
        años = player_state.get('años_experiencia', 0)

        return skill > 0 or años > 0
