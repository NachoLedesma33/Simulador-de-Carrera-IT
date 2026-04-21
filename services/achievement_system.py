import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    condition: Dict[str, Any]
    message: str
    icon: str
    category: str
    puntos: int


class AchievementSystem:
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: List[str] = []
        self.achievement_stats: Dict[str, int] = {}
        self._init_stats()

    def _init_stats(self):
        self.achievement_stats = {
            'total_achievements': 0,
            'unlocked_count': 0,
            'points_earned': 0,
            'by_category': {}
        }

    def load_achievements(self, filepath: str = 'data/achievements.yaml'):
        path = Path(filepath)
        if not path.exists():
            path = Path(__file__).parent.parent / filepath

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            achievements_data = data.get('achievements', {})

            for ach_id, ach_data in achievements_data.items():
                ach_data['id'] = ach_id
                achievement = Achievement(
                    id=ach_data.get('id', ''),
                    name=ach_data.get('name', ''),
                    description=ach_data.get('description', ''),
                    condition=ach_data.get('condition', {}),
                    message=ach_data.get('message', ''),
                    icon=ach_data.get('icon', '🏆'),
                    category=ach_data.get('category', 'general'),
                    puntos=ach_data.get('puntos', 0)
                )
                self.achievements[achievement.id] = achievement

            self.achievement_stats['total_achievements'] = len(self.achievements)
            logger.info(f'Achievements cargados: {len(self.achievements)}')
            return len(self.achievements)

        except Exception as e:
            logger.error(f'Error cargando achievements: {e}')
            return 0

    def check_and_unlock(self, player_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        newly_unlocked = []

        for ach_id, achievement in self.achievements.items():
            if ach_id in self.unlocked_achievements:
                continue

            if self._check_condition(achievement.condition, player_state):
                self.unlocked_achievements.append(ach_id)
                self.achievement_stats['unlocked_count'] += 1
                self.achievement_stats['points_earned'] += achievement.puntos

                category = achievement.category
                self.achievement_stats['by_category'][category] = \
                    self.achievement_stats['by_category'].get(category, 0) + 1

                newly_unlocked.append({
                    'id': ach_id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'message': achievement.message,
                    'icon': achievement.icon,
                    'puntos': achievement.puntos,
                    'category': achievement.category
                })

                logger.info(f'Achievement unlocked: {achievement.name}')

        return newly_unlocked

    def _check_condition(self, condition: Dict[str, Any], player_state: Dict[str, Any]) -> bool:
        condition_type = condition.get('type')

        if condition_type == 'stack_count':
            required = condition.get('value', 0)
            stack = player_state.get('stack', [])
            return len(stack) >= required

        if condition_type == 'stack_categories':
            required_cats = condition.get('categories', [])
            stack = player_state.get('stack', [])

            frontend = ['HTML', 'CSS', 'JavaScript', 'React', 'Vue.js', 'Angular', 'TypeScript']
            backend = ['Python', 'Java', 'Node.js', 'Go', 'Rust', 'Ruby', 'PHP', 'Django', 'Flask']
            database = ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis']

            has_frontend = any(tech in stack for tech in frontend)
            has_backend = any(tech in stack for tech in backend)
            has_database = any(tech in stack for tech in database)

            return ('frontend' in required_cats and has_frontend or 'frontend' not in required_cats) and \
                   ('backend' in required_cats and has_backend or 'backend' not in required_cats) and \
                   ('database' in required_cats and has_database or 'database' not in required_cats)

        if condition_type == 'stack_tech':
            techs = condition.get('techs', [])
            stack = player_state.get('stack', [])
            return any(tech in stack for tech in techs)

        if condition_type == 'nivel':
            required = condition.get('value', '')
            nivel = player_state.get('nivel', '')
            return nivel == required

        if condition_type == 'level_up':
            current_level = player_state.get('nivel', '')
            from_level = condition.get('from_level', '')
            to_level = condition.get('to_level', '')
            niveles = ['trainee', 'junior', 'semi-senior', 'senior', 'lead']
            if current_level == to_level:
                return True
            return False

        if condition_type == 'career_speed':
            required_nivel = condition.get('nivel', '')
            max_years = condition.get('max_years', 10)
            nivel = player_state.get('nivel', '')
            años = player_state.get('años_experiencia', 0)
            return nivel == required_nivel and años < max_years

        if condition_type == 'experiencia':
            required = condition.get('value', 0)
            años = player_state.get('años_experiencia', 0)
            return años >= required

        if condition_type == 'decisiones_count':
            required = condition.get('value', 0)
            decisiones = player_state.get('decisiones_tomadas', [])
            return len(decisiones) >= required

        if condition_type == 'reputacion':
            required = condition.get('value', 0)
            reputacion = player_state.get('reputacion', 0)
            return reputacion >= required

        if condition_type == 'salario':
            required = condition.get('value', 0)
            salario = player_state.get('salario', 0)
            return salario >= required

        if condition_type == 'salary_total':
            return False

        if condition_type == 'balance':
            max_stress = condition.get('max_stress', 100)
            min_skill = condition.get('min_skill', 0)
            stress = player_state.get('estres', 0)
            skill = player_state.get('skill_level', 0)
            return stress < max_stress and skill > min_skill

        if condition_type == 'high_stress_survived':
            return False

        if condition_type == 'low_stress_streak':
            return False

        if condition_type == 'positive_events_streak':
            return False

        if condition_type == 'crisis_survived':
            return False

        if condition_type == 'decisions_no_rest':
            return False

        return False

    def force_unlock(self, achievement_id: str, player_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return None

        if achievement_id in self.unlocked_achievements:
            return None

        if not self._check_condition(achievement.condition, player_state):
            return None

        self.unlocked_achievements.append(achievement_id)
        self.achievement_stats['unlocked_count'] += 1
        self.achievement_stats['points_earned'] += achievement.puntos

        return {
            'id': achievement_id,
            'name': achievement.name,
            'description': achievement.description,
            'message': achievement.message,
            'icon': achievement.icon,
            'puntos': achievement.puntos,
            'category': achievement.category
        }

    def get_unlocked_achievements(self) -> List[Dict[str, Any]]:
        result = []
        for ach_id in self.unlocked_achievements:
            ach = self.achievements.get(ach_id)
            if ach:
                result.append({
                    'id': ach_id,
                    'name': ach.name,
                    'description': ach.description,
                    'icon': ach.icon,
                    'puntos': ach.puntos,
                    'category': ach.category
                })
        return result

    def get_locked_achievements(self) -> List[Dict[str, Any]]:
        result = []
        for ach_id, ach in self.achievements.items():
            if ach_id not in self.unlocked_achievements:
                result.append({
                    'id': ach_id,
                    'name': ach.name,
                    'description': ach.description,
                    'icon': ach.icon,
                    'puntos': ach.puntos,
                    'category': ach.category
                })
        return result

    def get_achievement_stats(self) -> Dict[str, Any]:
        return {
            **self.achievement_stats,
            'percentage': (self.achievement_stats['unlocked_count'] / max(1, self.achievement_stats['total_achievements'])) * 100
        }

    def reset(self):
        self.unlocked_achievements = []
        self._init_stats()
        self.achievement_stats['total_achievements'] = len(self.achievements)


def create_achievement_system() -> AchievementSystem:
    system = AchievementSystem()
    system.load_achievements()
    return system


def check_achievements(player_state: Dict[str, Any], achievement_system: Optional[AchievementSystem] = None) -> List[Dict[str, Any]]:
    if achievement_system is None:
        achievement_system = create_achievement_system()

    return achievement_system.check_and_unlock(player_state)
