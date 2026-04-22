import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Player, DecisionEngine
from services import (
    apply_stat_change,
    apply_add_tech,
    apply_add_achievement,
    save_player_to_session,
    load_player_from_session,
    clear_session,
)
from services.effect_applier import (
    apply_stat_change,
    apply_stat_set,
    apply_add_tech,
    apply_remove_tech,
    apply_add_achievement,
    apply_effects_batch,
)
from services.session_manager import migrate_session
from services.event_system import EventSystem
from services.achievement_system import AchievementSystem
from utils import (
    validate_player_state,
    can_make_decision,
    validate_decision_transition,
    sanitize_player_state,
)
from utils.career_paths import (
    get_career_trajectory,
    calculate_salary_multiplier,
    get_next_milestone,
    generate_career_advice,
)


@pytest.fixture
def player():
    return Player(
        nombre="Test Player",
        nivel="trainee",
        skill_level=25,
        salario=20000,
        estres=30,
        reputacion=15,
        stack=["Python", "JavaScript"],
        logros=[],
        decisiones_tomadas=[],
        años_experiencia=1.0
    )


@pytest.fixture
def player_dict():
    return {
        'nombre': 'Test Player',
        'nivel': 'trainee',
        'skill_level': 25,
        'salario': 20000,
        'estres': 30,
        'reputacion': 15,
        'stack': ['Python', 'JavaScript'],
        'logros': [],
        'decisiones_tomadas': [],
        'años_experiencia': 1.0
    }


@pytest.fixture
def decision_engine():
    engine = DecisionEngine()
    engine.load_decisions()
    engine.load_events()
    return engine


@pytest.fixture
def event_system():
    es = EventSystem()
    es.load_events()
    return es


@pytest.fixture
def achievement_system():
    a = AchievementSystem()
    a.load_achievements()
    return a


class TestPlayerModel:
    def test_player_creation(self):
        player = Player()
        assert player.nivel == 'trainee'
        assert player.skill_level == 0
        assert player.salario == 15000
        assert player.estres == 0
        assert player.reputacion == 0
        assert player.stack == []
        assert player.logros == []

    def test_player_to_dict(self, player):
        data = player.to_dict()
        assert data['nivel'] == 'trainee'
        assert data['skill_level'] == 25
        assert data['salario'] == 20000

    def test_calculate_career_level(self, player):
        assert player.calculate_career_level() == 'junior'

        player.skill_level = 10
        assert player.calculate_career_level() == 'trainee'

        player.skill_level = 90
        assert player.calculate_career_level() == 'lead'

    def test_is_burned_out(self, player):
        assert not player.is_burned_out()

        player.estres = 85
        assert player.is_burned_out()

    def test_can_apply_to_next_level(self, player):
        player.skill_level = 25
        assert player.can_apply_to_next_level()

        player.skill_level = 10
        assert not player.can_apply_to_next_level()

    def test_add_tecnologia(self, player):
        player.stack = []
        player.add_tecnologia('React')
        assert 'React' in player.stack

        player.add_tecnologia('React')
        assert player.stack.count('React') == 1

    def test_add_logro(self, player):
        player.logros = []
        player.add_logro('First Win')
        assert 'First Win' in player.logros

        player.add_logro('First Win')
        assert player.logros.count('First Win') == 1

    def test_update_nivel(self, player):
        player.skill_level = 50
        player.salario = 20000
        player.update_nivel()

        assert player.nivel == 'semi-senior'
        assert player.salario > 20000


class TestEffectApplier:
    def test_apply_stat_change_positive(self):
        state = {'skill_level': 50}
        result = apply_stat_change(state, 'skill_level', 20)
        assert result.success
        assert state['skill_level'] == 70

    def test_apply_stat_change_negative(self):
        state = {'skill_level': 50}
        result = apply_stat_change(state, 'skill_level', -30)
        assert result.success
        assert state['skill_level'] == 20

    def test_apply_stat_change_clamping_upper(self):
        state = {'skill_level': 90}
        result = apply_stat_change(state, 'skill_level', 50)
        assert result.success
        assert state['skill_level'] == 100

    def test_apply_stat_change_clamping_lower(self):
        state = {'skill_level': 20}
        result = apply_stat_change(state, 'skill_level', -50)
        assert result.success
        assert state['skill_level'] == 0

    def test_apply_stat_change_estres(self):
        state = {'estres': 50}
        result = apply_stat_change(state, 'estres', 40)
        assert result.success
        assert state['estres'] == 90

    def test_apply_stat_change_estres_clamp(self):
        state = {'estres': 90}
        result = apply_stat_change(state, 'estres', 50)
        assert result.success
        assert state['estres'] == 100

    def test_apply_add_tech(self):
        state = {'stack': ['Python']}
        result = apply_add_tech(state, 'React')
        assert result.success
        assert 'React' in state['stack']

    def test_add_tech_no_duplicates(self):
        state = {'stack': ['Python']}
        result = apply_add_tech(state, 'Python')
        assert not result.success

    def test_apply_add_achievement(self):
        state = {'logros': []}
        result = apply_add_achievement(state, 'First Win')
        assert result.success
        assert 'First Win' in state['logros']

    def test_apply_add_achievement_no_duplicates(self):
        state = {'logros': ['First Win']}
        result = apply_add_achievement(state, 'First Win')
        assert not result.success

    def test_apply_effects_batch(self):
        state = {'skill_level': 30, 'salario': 20000, 'stack': []}
        effects = [
            {'type': 'stat_change', 'stat': 'skill_level', 'delta': 10},
            {'type': 'stat_change', 'stat': 'salario', 'delta': 5000},
            {'type': 'add_tech', 'add': 'Python'}
        ]
        results = apply_effects_batch(state, effects)
        assert state['skill_level'] == 40
        assert state['salario'] == 25000
        assert 'Python' in state['stack']


class TestDecisionEngine:
    def test_load_decisions(self, decision_engine):
        assert len(decision_engine.decisions) > 0
        assert 'inicio' in decision_engine.decisions

    def test_load_events(self, decision_engine):
        assert len(decision_engine.events) > 0

    def test_get_decision(self, decision_engine, player):
        decision = decision_engine.get_decision('inicio', player.to_dict())
        assert decision is not None
        assert decision['id'] == 'inicio'

    def test_get_decision_with_requirements(self, decision_engine):
        player_state = {'skill_level': 80, 'stack': [], 'reputacion': 50, 'años_experiencia': 3}
        decision = decision_engine.get_decision('decision_senior_1', player_state)
        assert decision is not None

    def test_get_available_options(self, decision_engine, player):
        options = decision_engine.get_available_options('inicio', player.to_dict())
        assert len(options) > 0

    def test_apply_effects(self, decision_engine):
        player_state = {'skill_level': 20, 'salario': 20000, 'estres': 20,
                       'reputacion': 10, 'stack': [], 'logros': [], 'años_experiencia': 1}
        updated = decision_engine.apply_effects('inicio', 0, player_state)
        assert 'skill_level' in updated
        assert 'estres' in updated

    def test_get_next_decision(self, decision_engine):
        player_state = {'skill_level': 20, 'salario': 20000, 'estres': 20,
                       'reputacion': 10, 'stack': [], 'logros': [], 'años_experiencia': 1}
        next_node = decision_engine.get_next_decision('inicio', 0, player_state)
        assert next_node is not None

    def test_is_final_decision(self, decision_engine):
        assert decision_engine.is_final_decision('final_victory')
        assert decision_engine.is_final_decision('final_burnout')
        assert not decision_engine.is_final_decision('inicio')


class TestValidators:
    def test_validate_player_state_valid(self, player):
        validation = validate_player_state(player)
        assert validation['valid']

    def test_validate_player_state_invalid_level(self, player_dict):
        player_dict['nivel'] = 'super_senior'
        validation = validate_player_state(player_dict)
        assert not validation['valid']

    def test_validate_player_state_burnout_warning(self, player_dict):
        player_dict['estres'] = 85
        player = Player(**player_dict)
        validation = validate_player_state(player)
        assert any('estr' in w.lower() for w in validation['warnings'])

    def test_can_make_decision_skill(self, player):
        requirements = {'skill_min': 20}
        result = can_make_decision(player, requirements)
        assert result['can_make']

    def test_can_make_decision_skill_fail(self, player):
        requirements = {'skill_min': 50}
        result = can_make_decision(player, requirements)
        assert not result['can_make']

    def test_can_make_decision_stack(self, player):
        requirements = {'stack': 'Python'}
        result = can_make_decision(player, requirements)
        assert result['can_make']

    def test_can_make_decision_stack_fail(self, player):
        requirements = {'stack': 'Rust'}
        result = can_make_decision(player, requirements)
        assert not result['can_make']

    def test_sanitize_player_state(self, player_dict):
        player_dict['skill_level'] = 150
        player_dict['estres'] = -10
        player_dict['nivel'] = 'invalid_level'
        sanitized = sanitize_player_state(player_dict)
        assert sanitized['skill_level'] == 100
        assert sanitized['estres'] == 0
        assert sanitized['nivel'] == 'trainee'


class TestEventSystem:
    def test_load_events(self, event_system):
        assert len(event_system.events) > 0

    def test_trigger_random_event(self, event_system):
        player_state = {
            'skill_level': 50,
            'salario': 30000,
            'estres': 30,
            'reputacion': 40,
            'stack': ['Python'],
            'logros': [],
            'años_experiencia': 2
        }
        result = event_system.trigger_random_event(player_state)
        assert result is None or 'event_id' in result

    def test_check_conditions(self, event_system):
        requirements = {'skill_min': 50}
        player_state = {'skill_level': 60}
        assert event_system.check_conditions(requirements, player_state)

        player_state = {'skill_level': 40}
        assert not event_system.check_conditions(requirements, player_state)


class TestAchievementSystem:
    def test_load_achievements(self, achievement_system):
        assert len(achievement_system.achievements) > 0

    def test_check_stack_master(self, achievement_system):
        player_state = {
            'stack': ['Python', 'JavaScript', 'React', 'Django', 'SQL'],
            'nivel': 'junior',
            'skill_level': 30,
            'reputacion': 20,
            'años_experiencia': 1,
            'logros': [],
            'decisiones_tomadas': [],
            'salario': 25000,
            'estres': 30
        }
        unlocked = achievement_system.check_and_unlock(player_state)
        stack_achievements = [a['id'] for a in unlocked]
        assert 'stack_master' in stack_achievements

    def test_check_full_stack_hero(self, achievement_system):
        player_state = {
            'stack': ['React', 'JavaScript', 'Python', 'Django', 'SQL', 'PostgreSQL'],
            'nivel': 'junior',
            'skill_level': 40,
            'reputacion': 30,
            'años_experiencia': 2,
            'logros': [],
            'decisiones_tomadas': [],
            'salario': 30000,
            'estres': 40
        }
        unlocked = achievement_system.check_and_unlock(player_state)
        achievement_ids = [a['id'] for a in unlocked]
        assert 'full_stack_hero' in achievement_ids

    def test_achievement_stats(self, achievement_system):
        player_state = {
            'stack': ['Python'],
            'nivel': 'junior',
            'skill_level': 30,
            'reputacion': 80,
            'años_experiencia': 1,
            'logros': [],
            'decisiones_tomadas': [],
            'salario': 30000,
            'estres': 30
        }
        achievement_system.check_and_unlock(player_state)
        stats = achievement_system.get_achievement_stats()
        assert stats['unlocked_count'] > 0


class TestCareerPaths:
    def test_get_career_trajectory_specialist(self):
        player_state = {
            'decisiones_tomadas': [],
            'stack': ['Python', 'JavaScript', 'React'],
            'skill_level': 85,
            'reputacion': 50,
            'años_experiencia': 6
        }
        trajectory = get_career_trajectory(player_state)
        assert trajectory == 'especialista'

    def test_get_career_trajectory_manager(self):
        player_state = {
            'decisiones_tomadas': [{'option_label': 'Liderar equipo'}],
            'stack': ['Python'],
            'skill_level': 50,
            'reputacion': 60,
            'años_experiencia': 3
        }
        trajectory = get_career_trajectory(player_state)
        assert trajectory == 'manager'

    def test_calculate_salary_multiplier(self):
        player_state = {
            'skill_level': 80,
            'reputacion': 80,
            'stack': ['AI/ML', 'Python', 'Kubernetes'],
            'nivel': 'senior',
            'logros': ['First Win']
        }
        multiplier = calculate_salary_multiplier(player_state)
        assert multiplier > 1.5

    def test_get_next_milestone(self):
        player_state = {
            'skill_level': 30,
            'nivel': 'junior',
            'años_experiencia': 1
        }
        milestone = get_next_milestone(player_state)
        assert milestone is not None

    def test_generate_career_advice_high_stress(self):
        player_state = {
            'skill_level': 50,
            'estres': 85,
            'reputacion': 30,
            'stack': ['Python'],
            'años_experiencia': 2,
            'nivel': 'junior'
        }
        advice = generate_career_advice(player_state)
        assert any(a.title == 'Gestionar el Estrés' for a in advice)

    def test_generate_career_advice_low_skill(self):
        player_state = {
            'skill_level': 20,
            'estres': 20,
            'reputacion': 10,
            'stack': [],
            'años_experiencia': 0.5,
            'nivel': 'trainee'
        }
        advice = generate_career_advice(player_state)
        assert any(a.title == 'Desarrollar Habilidades Técnicas' for a in advice)


class TestIntegration:
    def test_full_player_lifecycle(self, player, decision_engine):
        state = player.to_dict()
        import copy
        new_state = copy.deepcopy(state)

        options = decision_engine.get_available_options('inicio', new_state)
        assert len(options) > 0

        updated_state = decision_engine.apply_effects('inicio', 0, new_state)
        assert updated_state != state

    def test_validation_after_effects(self, player):
        state = player.to_dict()
        state['skill_level'] = 150
        state['estres'] = -20

        sanitized = sanitize_player_state(state)
        assert sanitized['skill_level'] <= 100
        assert sanitized['estres'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
