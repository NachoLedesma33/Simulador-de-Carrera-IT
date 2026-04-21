import random
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class EventCondition:
    stat: str
    operator: str
    value: float


@dataclass
class EventEffect:
    stat: str
    delta: Optional[float] = None
    set_value: Optional[Any] = None
    add_item: Optional[str] = None
    remove_item: Optional[str] = None
    logro: Optional[str] = None
    trigger: Optional[str] = None
    temporary: bool = False
    duration: int = 0


@dataclass
class GameEvent:
    id: str
    titulo: str
    descripcion: str
    tipo: str
    probabilidad: float
    efectos: List[Dict[str, Any]]
    requerimientos: Dict[str, Any] = field(default_factory=dict)
    cooldown: int = 0
    can_repeat: bool = True
    mensaje: str = ""
    is_positive: bool = False
    is_negative: bool = False
    is_risk: bool = False


class EventSystem:
    def __init__(self):
        self.events: Dict[str, GameEvent] = {}
        self.triggered_events: List[Dict[str, Any]] = []
        self.active_temporary_effects: Dict[str, List[Dict[str, Any]]] = {}
        self.event_cooldowns: Dict[str, datetime] = {}
        self.notification_callback: Optional[Callable] = None

    def load_events(self, filepath: str = 'data/events.yaml'):
        import yaml
        from pathlib import Path

        path = Path(filepath)
        if not path.exists():
            path = Path(__file__).parent.parent / filepath

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            eventos_data = data.get('eventos_aleatorios', {})

            for event_id, event_data in eventos_data.items():
                event_data['id'] = event_id
                event = self._parse_event(event_data)
                self.events[event.id] = event

            logger.info(f'Eventos cargados: {len(self.events)}')
            return len(self.events)

        except Exception as e:
            logger.error(f'Error cargando eventos: {e}')
            return 0

    def _parse_event(self, data: Dict[str, Any]) -> GameEvent:
        return GameEvent(
            id=data.get('id', ''),
            titulo=data.get('titulo', ''),
            descripcion=data.get('descripcion', ''),
            tipo=data.get('tipo', 'neutral'),
            probabilidad=data.get('probabilidad', 0.1),
            efectos=data.get('efectos', []),
            requerimientos=data.get('requerimientos', {}),
            mensaje=data.get('mensaje', ''),
            is_positive=data.get('tipo') == 'positivo',
            is_negative=data.get('tipo') == 'negativo',
            is_risk=data.get('tipo') == 'riesgo'
        )

    def set_notification_callback(self, callback: Callable):
        self.notification_callback = callback

    def send_notification(self, event: GameEvent, effects_applied: List[str]):
        if self.notification_callback:
            self.notification_callback({
                'event': event,
                'effects': effects_applied,
                'title': event.titulo,
                'description': event.descripcion,
                'message': event.mensaje,
                'tipo': event.tipo
            })

    def check_conditions(self, requirements: Dict[str, Any], player_state: Dict[str, Any]) -> bool:
        if not requirements:
            return True

        skill_min = requirements.get('skill_min')
        if skill_min is not None:
            if player_state.get('skill_level', 0) < skill_min:
                return False

        skill_max = requirements.get('skill_max')
        if skill_max is not None:
            if player_state.get('skill_level', 0) > skill_max:
                return False

        reputacion_min = requirements.get('reputacion_min')
        if reputacion_min is not None:
            if player_state.get('reputacion', 0) < reputacion_min:
                return False

        stres_min = requirements.get('estres_min')
        if stres_min is not None:
            if player_state.get('estres', 0) < stres_min:
                return False

        stres_max = requirements.get('estres_max')
        if stres_max is not None:
            if player_state.get('estres', 0) > stres_max:
                return False

        años_min = requirements.get('años_experiencia_min')
        if años_min is not None:
            if player_state.get('años_experiencia', 0) < años_min:
                return False

        nivel = requirements.get('nivel')
        if nivel is not None:
            if player_state.get('nivel') != nivel:
                return False

        stack_required = requirements.get('stack')
        if stack_required is not None:
            if stack_required not in player_state.get('stack', []):
                return False

        stack_min = requirements.get('stack_min')
        if stack_min is not None:
            if len(player_state.get('stack', [])) < stack_min:
                return False

        flag_required = requirements.get('flag')
        if flag_required is not None:
            flags = player_state.get('flags', {})
            if not flags.get(flag_required, False):
                return False

        return True

    def is_on_cooldown(self, event_id: str) -> bool:
        if event_id not in self.event_cooldowns:
            return False

        event = self.events.get(event_id)
        if not event or event.cooldown == 0:
            return False

        cooldown_time = self.event_cooldowns[event_id]
        if datetime.now() > cooldown_time:
            del self.event_cooldowns[event_id]
            return False

        return True

    def trigger_random_event(self, player_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        available_events = []

        for event_id, event in self.events.items():
            if not event.can_repeat and event_id in [e['id'] for e in self.triggered_events]:
                continue

            if self.is_on_cooldown(event_id):
                continue

            if not self.check_conditions(event.requerimientos, player_state):
                continue

            if random.random() < event.probabilidad:
                available_events.append(event)

        if not available_events:
            return None

        selected_event = random.choice(available_events)
        return self._apply_event(selected_event, player_state)

    def _apply_event(self, event: GameEvent, player_state: Dict[str, Any]) -> Dict[str, Any]:
        effects_applied = []

        for efecto in event.efectos:
            stat = efecto.get('stat')
            delta = efecto.get('delta')
            set_value = efecto.get('set')
            add_item = efecto.get('add')
            remove_item = efecto.get('remove')
            logro = efecto.get('logro')

            if stat in player_state:
                if delta is not None:
                    current = player_state.get(stat, 0)
                    new_value = current + delta

                    if stat in ['skill_level', 'estres', 'reputacion']:
                        new_value = max(0, min(100, new_value))
                    elif stat == 'salario':
                        new_value = max(0, min(50000, new_value))

                    player_state[stat] = new_value
                    effects_applied.append(f'{stat}: {current} → {new_value}')

                elif set_value is not None:
                    player_state[stat] = set_value
                    effects_applied.append(f'{stat} = {set_value}')

            if add_item:
                if 'stack' not in player_state:
                    player_state['stack'] = []
                if add_item not in player_state['stack']:
                    player_state['stack'].append(add_item)
                    effects_applied.append(f'Tech añadida: {add_item}')

            if remove_item:
                if 'stack' in player_state and remove_item in player_state['stack']:
                    player_state['stack'].remove(remove_item)
                    effects_applied.append(f'Tech eliminada: {remove_item}')

            if logro:
                if 'logros' not in player_state:
                    player_state['logros'] = []
                if logro not in player_state['logros']:
                    player_state['logros'].append(logro)
                    effects_applied.append(f'🏆 Logro: {logro}')

        self.triggered_events.append({
            'id': event.id,
            'timestamp': datetime.now().isoformat(),
            'effects': effects_applied
        })

        if event.cooldown > 0:
            self.event_cooldowns[event.id] = datetime.now() + timedelta(hours=event.cooldown)

        result = {
            'event_id': event.id,
            'titulo': event.titulo,
            'descripcion': event.descripcion,
            'tipo': event.tipo,
            'mensaje': event.mensaje,
            'effects_applied': effects_applied,
            'player_state': player_state
        }

        self.send_notification(event, effects_applied)

        logger.info(f'Evento triggered: {event.id} - {event.titulo}')
        return result

    def force_trigger_event(self, event_id: str, player_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        event = self.events.get(event_id)
        if not event:
            return None

        if not self.check_conditions(event.requerimientos, player_state):
            logger.warning(f'Evento {event_id} no puede ser aplicado: condiciones no cumplidas')
            return None

        return self._apply_event(event, player_state)

    def get_available_events(self, player_state: Dict[str, Any]) -> List[GameEvent]:
        available = []

        for event_id, event in self.events.items():
            if not event.can_repeat and event_id in [e['id'] for e in self.triggered_events]:
                continue

            if self.is_on_cooldown(event_id):
                continue

            if self.check_conditions(event.requerimientos, player_state):
                available.append(event)

        return available

    def get_event_by_id(self, event_id: str) -> Optional[GameEvent]:
        return self.events.get(event_id)

    def get_triggered_events(self) -> List[Dict[str, Any]]:
        return self.triggered_events

    def clear_history(self):
        self.triggered_events = []
        self.event_cooldowns = {}

    def get_event_stats(self) -> Dict[str, Any]:
        stats = {
            'total_events': len(self.events),
            'triggered_count': len(self.triggered_events),
            'by_type': {},
            'recent_events': self.triggered_events[-5:] if self.triggered_events else []
        }

        for event in self.triggered_events:
            event_type = event.get('tipo', 'unknown')
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1

        return stats


def create_event_system() -> EventSystem:
    system = EventSystem()
    system.load_events()
    return system


def trigger_random_event(player_state: Dict[str, Any], event_system: Optional[EventSystem] = None) -> Optional[Dict[str, Any]]:
    if event_system is None:
        event_system = create_event_system()

    return event_system.trigger_random_event(player_state)
