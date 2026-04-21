import random
from typing import Dict, Any, List
from models import Player
from services import save_player_to_session, set_current_decision_id


BUILDS = {
    'backend_specialist': {
        'nombre': 'Backend Dev',
        'nivel': 'semi-senior',
        'skill_level': 55,
        'salario': 48000,
        'estres': 35,
        'reputacion': 45,
        'stack': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
        'años_experiencia': 3.5,
        'logros': ['Backend Ninja', 'DB Master'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Busqueda de primer empleo'},
            {'decision_id': 'primera_entrevista', 'option_label': 'Me interesa el desarrollo backend'},
            {'decision_id': 'especializacion_backend_1', 'option_label': 'Profundizar en Python'},
            {'decision_id': 'arquitectura_1', 'option_label': 'Arquitectura robusta'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar promoción'},
            {'decision_id': 'decision_carrera_1', 'option_label': 'Ir a una empresa establecida'},
        ]
    },
    'frontend_master': {
        'nombre': 'Frontend Pro',
        'nivel': 'senior',
        'skill_level': 78,
        'salario': 72000,
        'estres': 55,
        'reputacion': 70,
        'stack': ['JavaScript', 'React', 'TypeScript', 'Vue.js', 'CSS', 'Next.js'],
        'años_experiencia': 5.2,
        'logros': ['React Ninja', 'UI Master', 'Code Reviewer'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Prácticas para ganar experiencia'},
            {'decision_id': 'primera_entrevista', 'option_label': 'Me interesa el desarrollo frontend'},
            {'decision_id': 'especializacion_frontend_1', 'option_label': 'Masterizar React'},
            {'decision_id': 'proyecto_portfolio_1', 'option_label': 'Aceptar proyecto open source'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar promoción'},
            {'decision_id': 'decision_tech_1', 'option_label': 'Convertirme en experto'},
        ]
    },
    'full_stack': {
        'nombre': 'Full Stack Dev',
        'nivel': 'semi-senior',
        'skill_level': 62,
        'salario': 52000,
        'estres': 60,
        'reputacion': 55,
        'stack': ['JavaScript', 'React', 'Python', 'Django', 'PostgreSQL', 'MongoDB', 'Docker'],
        'años_experiencia': 4.0,
        'logros': ['Full Stack Hero', 'Versatile Dev'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Busqueda de empleo'},
            {'decision_id': 'primera_entrevista', 'option_label': 'Me interesa el backend'},
            {'decision_id': 'especializacion_backend_1', 'option_label': 'Profundizar en Python'},
            {'decision_id': 'especializacion_frontend_1', 'option_label': 'Aprender múltiples tecnologías'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar promoción'},
        ]
    },
    'manager': {
        'nombre': 'Tech Manager',
        'nivel': 'lead',
        'skill_level': 85,
        'salario': 95000,
        'estres': 75,
        'reputacion': 85,
        'stack': ['JavaScript', 'Python', 'Agile', 'Scrum', 'AWS', 'Leadership'],
        'años_experiencia': 7.5,
        'logros': ['Team Lead', 'Mentor', 'Agile Coach', 'CTO Ready'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Busqueda de empleo'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar promoción'},
            {'decision_id': 'decision_liderazgo_1', 'option_label': 'Aceptar rol de Team Lead'},
            {'decision_id': 'decision_final_senior', 'option_label': 'Buscar rol de Lead'},
        ]
    },
    'freelancer': {
        'nombre': 'Freelancer Pro',
        'nivel': 'senior',
        'skill_level': 72,
        'salario': 85000,
        'estres': 65,
        'reputacion': 80,
        'stack': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Firebase', 'Stripe'],
        'años_experiencia': 4.8,
        'logros': ['Freelancer', 'Client Master', 'Indie Hacker'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Prácticas'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar promoción'},
            {'decision_id': 'decision_freelance_1', 'option_label': 'Aceptar proyecto freelance'},
        ]
    },
    'startup_founder': {
        'nombre': 'Startup Founder',
        'nivel': 'senior',
        'skill_level': 80,
        'salario': 35000,
        'estres': 90,
        'reputacion': 75,
        'stack': ['Python', 'React', 'AWS', 'Docker', 'Kubernetes', 'Fundraising'],
        'años_experiencia': 5.0,
        'logros': ['Emprendedor', 'First Hire', 'Seed Round'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Empleo en startup'},
            {'decision_id': 'decision_riesgo_1', 'option_label': 'Emprender tiempo completo'},
        ]
    },
    'burnout_warning': {
        'nombre': 'Burned Out Dev',
        'nivel': 'senior',
        'skill_level': 85,
        'salario': 75000,
        'estres': 85,
        'reputacion': 60,
        'stack': ['JavaScript', 'React', 'Python', 'Docker'],
        'años_experiencia': 6.0,
        'logros': ['Survivor', 'Hard Worker'],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Busqueda de empleo'},
            {'decision_id': 'promo_junior', 'option_label': 'Aceptar'},
            {'decision_id': 'decision_senior_1', 'option_label': 'Buscar promoción'},
        ]
    },
    'newbie': {
        'nombre': 'New Developer',
        'nivel': 'trainee',
        'skill_level': 15,
        'salario': 18000,
        'estres': 25,
        'reputacion': 10,
        'stack': ['HTML', 'CSS', 'JavaScript'],
        'años_experiencia': 0.5,
        'logros': [],
        'decisiones_tomadas': [
            {'decision_id': 'inicio', 'option_label': 'Prácticas'},
            {'decision_id': 'primera_entrevista', 'option_label': 'Frontend'},
        ]
    },
}


DECISION_TRAJECTORY = {
    'backend_specialist': [
        'inicio',
        'primera_entrevista',
        'especializacion_backend_1',
        'arquitectura_1',
        'promo_junior',
        'decision_carrera_1',
        'decision_senior_1',
        'decision_final_senior'
    ],
    'frontend_master': [
        'inicio',
        'primera_entrevista',
        'especializacion_frontend_1',
        'proyecto_portfolio_1',
        'promo_junior',
        'decision_tech_1',
        'decision_senior_1',
        'decision_final_senior'
    ],
    'full_stack': [
        'inicio',
        'primera_entrevista',
        'especializacion_backend_1',
        'especializacion_frontend_1',
        'promo_junior',
        'decision_tech_1'
    ],
    'manager': [
        'inicio',
        'primera_entrevista',
        'especializacion_backend_1',
        'promo_junior',
        'decision_liderazgo_1',
        'decision_final_senior',
        'decision_cto'
    ],
    'freelancer': [
        'inicio',
        'primera_entrevista',
        'especializacion_frontend_1',
        'promo_junior',
        'decision_freelance_1',
        'decision_tech_1',
        'decision_final_senior'
    ],
    'startup_founder': [
        'inicio',
        'primera_entrevista',
        'decision_carrera_1',
        'decision_freelance_1',
        'decision_riesgo_1'
    ],
    'burnout_warning': [
        'inicio',
        'primera_entrevista',
        'especializacion_backend_1',
        'promo_junior',
        'decision_senior_1',
        'decision_final_senior'
    ],
    'newbie': [
        'inicio'
    ]
}


def create_player_from_build(build_data: Dict[str, Any]) -> Player:
    return Player(
        nombre=build_data.get('nombre', 'Player'),
        nivel=build_data.get('nivel', 'trainee'),
        skill_level=build_data.get('skill_level', 0),
        salario=build_data.get('salario', 15000),
        estres=build_data.get('estres', 0),
        reputacion=build_data.get('reputacion', 0),
        stack=build_data.get('stack', []),
        logros=build_data.get('logros', []),
        decisiones_tomadas=build_data.get('decisiones_tomadas', []),
        años_experiencia=build_data.get('años_experiencia', 0.0)
    )


def seed_demo_game(build_type: str = 'full_stack') -> Dict[str, Any]:
    if build_type not in BUILDS:
        available = ', '.join(BUILDS.keys())
        raise ValueError(f"Tipo de build '{build_type}' no válido. Disponibles: {available}")

    build_data = BUILDS[build_type].copy()
    player = create_player_from_build(build_data)

    try:
        save_player_to_session(player)

        trajectory = DECISION_TRAJECTORY.get(build_type, ['inicio'])
        current_decision = trajectory[-1] if trajectory else 'inicio'
        set_current_decision_id(current_decision)
    except RuntimeError:
        pass

    return {
        'success': True,
        'build_type': build_type,
        'player': player.to_dict(),
        'current_decision': trajectory[-1] if trajectory else 'inicio',
        'message': f'Partida de demostración creada: {build_data.get("nombre")}'
    }


def get_available_builds() -> List[Dict[str, Any]]:
    return [
        {
            'id': key,
            'nombre': data.get('nombre'),
            'nivel': data.get('nivel'),
            'skill_level': data.get('skill_level'),
            'descripcion': f"Nivel: {data.get('nivel')}, Skill: {data.get('skill_level')}"
        }
        for key, data in BUILDS.items()
    ]


def get_random_build() -> str:
    return random.choice(list(BUILDS.keys()))


def create_custom_build(
    nombre: str = 'Custom Player',
    nivel: str = 'trainee',
    skill_level: int = 0,
    stres: int = 0,
    reputacion: int = 0,
    stack: List[str] = None,
    años_experiencia: float = 0.0
) -> Player:
    if stack is None:
        stack = []

    player = Player(
        nombre=nombre,
        nivel=nivel,
        skill_level=max(0, min(100, skill_level)),
        salario=15000,
        estres=max(0, min(100, stres)),
        reputacion=max(0, min(100, reputacion)),
        stack=stack,
        años_experiencia=años_experiencia,
        logros=[],
        decisiones_tomadas=[]
    )

    return player


def get_build_summary(build_type: str) -> Dict[str, Any]:
    if build_type not in BUILDS:
        return {'error': 'Build no encontrado'}

    build = BUILDS[build_type]
    return {
        'nombre': build.get('nombre'),
        'nivel': build.get('nivel'),
        'skill': build.get('skill_level'),
        'salario': build.get('salario'),
        'estres': build.get('estres'),
        'reputacion': build.get('reputacion'),
        'stack': build.get('stack'),
        'logros': build.get('logros'),
        'años_experiencia': build.get('años_experiencia'),
        'trayectoria': DECISION_TRAJECTORY.get(build_type, [])
    }


if __name__ == '__main__':
    print("=== Simulador IT - Seed Data ===")
    print("\nBuilds disponibles:")
    for build in get_available_builds():
        print(f"  - {build['id']}: {build['descripcion']}")

    print("\nEjemplo de uso:")
    print("  from services.seed_data import seed_demo_game")
    print("  result = seed_demo_game('full_stack')")
