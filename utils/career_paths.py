import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from models.player import LEVELS


@dataclass
class CareerMilestone:
    name: str
    description: str
    skill_required: int
    nivel: str
    salary_target: int
    experiencia_years: float


@dataclass
class CareerAdvice:
    priority: int
    title: str
    description: str
    action: str
    impact: str


CAREER_MILESTONES = {
    'trainee': CareerMilestone(
        name='Primer Empleo',
        description='Consigue tu primer trabajo como trainee en una empresa tech',
        skill_required=10,
        nivel='trainee',
        salary_target=15000,
        experiencia_years=0.5
    ),
    'junior': CareerMilestone(
        name='Junior Developer',
        description='Consigue el título de Junior y tu primer aumento',
        skill_required=25,
        nivel='junior',
        salary_target=30000,
        experiencia_years=1.0
    ),
    'semi_senior': CareerMilestone(
        name='Semi-Senior Developer',
        description='Alcanza el nivel intermedio con mejor salario',
        skill_required=50,
        nivel='semi-senior',
        salary_target=45000,
        experiencia_years=2.5
    ),
    'senior': CareerMilestone(
        name='Senior Developer',
        description='Conviértete en experto reconocido',
        skill_required=75,
        nivel='senior',
        salary_target=70000,
        experiencia_years=5.0
    ),
    'lead': CareerMilestone(
        name='Tech Lead / CTO',
        description='Alcanza la cima de tu carrera técnica',
        skill_required=90,
        nivel='lead',
        salary_target=100000,
        experiencia_years=8.0
    ),
    'first_job': CareerMilestone(
        name='Primera Entrevista',
        description='Prepara tu CV y practica para entrevistas técnicas',
        skill_required=5,
        nivel='trainee',
        salary_target=10000,
        experiencia_years=0.1
    ),
    'open_source': CareerMilestone(
        name='Contribuidor Open Source',
        description='Contribuye a un proyecto open source',
        skill_required=30,
        nivel='junior',
        salary_target=35000,
        experiencia_years=1.5
    ),
    'certification': CareerMilestone(
        name='Certificación Técnica',
        description='Obtén una certificación profesional',
        skill_required=40,
        nivel='junior',
        salary_target=40000,
        experiencia_years=1.0
    ),
    'team_lead': CareerMilestone(
        name='Liderazgo de Equipo',
        description='Lidera un equipo de desarrolladores',
        skill_required=60,
        nivel='semi-senior',
        salary_target=60000,
        experiencia_years=3.0
    ),
    'conference': CareerMilestone(
        name='Speaker en Conferencia',
        description='Comparte tu conocimiento en una conferencia',
        skill_required=70,
        nivel='senior',
        salary_target=80000,
        experiencia_years=5.0
    ),
}


def get_career_trajectory(player_state: Dict[str, Any]) -> str:
    decisiones = player_state.get('decisiones_tomadas', [])
    stack = player_state.get('stack', [])
    skill = player_state.get('skill_level', 0)
    reputacion = player_state.get('reputacion', 0)
    años = player_state.get('años_experiencia', 0)

    if años >= 5 and skill >= 80:
        return 'especialista'
    elif any('lider' in d.get('option_label', '').lower() for d in decisiones):
        return 'manager'
    elif any('emprend' in d.get('option_label', '').lower() for d in decisiones):
        return 'emprendedor'
    elif any('freelance' in d.get('option_label', '').lower() for d in decisiones):
        return 'freelancer'
    elif any('startup' in d.get('option_label', '').lower() for d in decisiones):
        return 'emprendedor'
    elif skill >= 60 and len(stack) >= 3:
        return 'especialista'
    elif reputacion >= 50 and años >= 2:
        return 'manager'
    else:
        return 'freelancer'


def calculate_salary_multiplier(player_state: Dict[str, Any]) -> float:
    base_multiplier = 1.0

    skill = player_state.get('skill_level', 0)
    if skill >= 80:
        base_multiplier *= 1.5
    elif skill >= 60:
        base_multiplier *= 1.3
    elif skill >= 40:
        base_multiplier *= 1.15
    elif skill >= 20:
        base_multiplier *= 1.0

    reputacion = player_state.get('reputacion', 0)
    if reputacion >= 70:
        base_multiplier *= 1.2
    elif reputacion >= 50:
        base_multiplier *= 1.1
    elif reputacion < 20:
        base_multiplier *= 0.9

    stack = player_state.get('stack', [])
    stack_multiplier = 1.0
    hot_techs = ['AI/ML', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Rust', 'Go', 'Kubernetes', 'AWS', 'GCP']
    in_demand = [tech for tech in stack if tech in hot_techs]
    stack_multiplier += len(in_demand) * 0.1

    popular_techs = ['React', 'Python', 'JavaScript', 'TypeScript', 'Docker', 'SQL']
    popular = [tech for tech in stack if tech in popular_techs]
    stack_multiplier += len(popular) * 0.05

    base_multiplier *= stack_multiplier

    nivel = player_state.get('nivel', 'trainee')
    level_multipliers = {
        'trainee': 1.0,
        'junior': 1.2,
        'semi-senior': 1.5,
        'senior': 1.8,
        'lead': 2.2
    }
    base_multiplier *= level_multipliers.get(nivel, 1.0)

    logros = player_state.get('logros', [])
    base_multiplier += len(logros) * 0.05

    return round(base_multiplier, 2)


def get_next_milestone(player_state: Dict[str, Any]) -> Optional[CareerMilestone]:
    skill = player_state.get('skill_level', 0)
    nivel = player_state.get('nivel', 'trainee')
    años = player_state.get('años_experiencia', 0)

    remaining_milestones = [
        milestone for _, milestone in CAREER_MILESTONES.items()
        if skill < milestone.skill_required or nivel != milestone.nivel
    ]

    if not remaining_milestones:
        return None

    remaining_milestones.sort(key=lambda m: m.skill_required)

    current_nivel_index = LEVELS.index(nivel) if nivel in LEVELS else 0

    next_milestone = None
    for milestone in remaining_milestones:
        if milestone.skill_required > skill:
            next_milestone = milestone
            break
        milestone_nivel_index = LEVELS.index(milestone.nivel) if milestone.nivel in LEVELS else 0
        if milestone_nivel_index > current_nivel_index:
            next_milestone = milestone
            break

    if next_milestone and skill >= next_milestone.skill_required:
        for milestone in remaining_milestones:
            milestone_nivel_index = LEVELS.index(milestone.nivel) if milestone.nivel in LEVELS else 0
            if milestone_nivel_index > current_nivel_index:
                next_milestone = milestone
                break

    return next_milestone


def get_milestone_progress(player_state: Dict[str, Any], milestone: CareerMilestone) -> float:
    if not milestone:
        return 100.0

    skill = player_state.get('skill_level', 0)
    skill_gap = milestone.skill_required - skill
    if skill_gap <= 0:
        return 100.0

    previous_required = 0
    for _, m in CAREER_MILESTONES.items():
        if m.skill_required < milestone.skill_required:
            previous_required = m.skill_required

    skill_progress = (skill - previous_required) / (milestone.skill_required - previous_required) * 100
    return max(0, min(100, skill_progress))


def generate_career_advice(player_state: Dict[str, Any]) -> List[CareerAdvice]:
    advice_list: List[CareerAdvice] = []

    skill = player_state.get('skill_level', 0)
    estres = player_state.get('estres', 0)
    reputacion = player_state.get('reputacion', 0)
    stack = player_state.get('stack', [])
    años = player_state.get('años_experiencia', 0)
    nivel = player_state.get('nivel', 'trainee')

    if estres > 70:
        advice_list.append(CareerAdvice(
            priority=1,
            title='Gestionar el Estrés',
            description=f'Tu nivel de estrés está en {estres}%. Es crucial tomar medidas.',
            action='Considera tomar un descanso, delegar tareas o reducir la carga de trabajo.',
            impact='Alto'
        ))

    if estres > 50 and estres <= 70:
        advice_list.append(CareerAdvice(
            priority=3,
            title='Balance Trabajo-Vida',
            description='Tu estrés está moderado. Mantén un balance saludable.',
            action='Practica técnicas de relajación y mantén límites claros.',
            impact='Medio'
        ))

    if skill < 30 and años < 1:
        advice_list.append(CareerAdvice(
            priority=2,
            title='Desarrollar Habilidades Técnicas',
            description=f'Skill actual: {skill}. Enfócate en aprender tecnologías específicas.',
            action='Dedica tiempo extra a estudiar y practicar código.',
            impact='Alto'
        ))

    if skill >= 30 and skill < 50 and len(stack) < 3:
        advice_list.append(CareerAdvice(
            priority=4,
            title='Expandir Tech Stack',
            description='Aprende nuevas tecnologías para ser más versátil.',
            action='Agrega al menos 2-3 tecnologías complementarias a tu stack.',
            impact='Medio'
        ))

    if reputacion < 30 and años >= 1:
        advice_list.append(CareerAdvice(
            priority=5,
            title='Construir Reputación',
            description=f'Reputación: {reputacion}. Participa en la comunidad.',
            action='Contribuye a proyectos open source o asiste a meetups.',
            impact='Medio'
        ))

    if años >= 2 and skill >= 50 and nivel != 'senior':
        advice_list.append(CareerAdvice(
            priority=2,
            title='Buscar Promoción',
            description='Tienes experiencia para subir de nivel.',
            action='Solicita más responsabilidades y habla con tu manager sobre promoción.',
            impact='Alto'
        ))

    if skill >= 60 and len(stack) >= 3:
        advice_list.append(CareerAdvice(
            priority=4,
            title='Especialización',
            description='Considera convertirte en experto en tu stack principal.',
            action='Profundiza en tecnologías clave y comparte conocimiento.',
            impact='Medio'
        ))

    if nivel == 'trainee' and skill >= 20:
        advice_list.append(CareerAdvice(
            priority=2,
            title='Buscar Primer Rol Junior',
            description='Estás listo para dar el salto a Junior.',
            action='Actualiza tu CV y postula a posiciones junior.',
            impact='Alto'
        ))

    current_stress = player_state.get('estres', 0)
    if current_stress < 30 and skill > 50:
        advice_list.append(CareerAdvice(
            priority=6,
            title='Oportunidades de Crecimiento',
            description='Estás en buena posición. Explora nuevas oportunidades.',
            action='Considera cambiar de trabajo o pedir un aumento.',
            impact='Bajo'
        ))

    if stack and len(stack) < 2:
        advice_list.append(CareerAdvice(
            priority=3,
            title='Fundamentos del Stack',
            description='Aprende al menos un lenguaje y una tecnología de base de datos.',
            action='Agrega SQL y un lenguaje como Python o JavaScript.',
            impact='Medio'
        ))

    advice_list.sort(key=lambda a: a.priority)

    return advice_list[:5]


def get_career_tips(career_type: str) -> List[str]:
    tips = {
        'especialista': [
            'Mantente actualizado con las últimas tecnologías.',
            'Dedica tiempo al aprendizaje continuo.',
            'Considera obtener certificaciones relevantes.',
            'Comparte conocimiento mediante blogs o talks.'
        ],
        'manager': [
            'Desarrolla habilidades de comunicación.',
            'Aprende sobre liderazgo y gestión de equipos.',
            'Balanza lo técnico con lo estratégico.',
            'Mentoriza a desarrolladores junior.'
        ],
        'emprendedor': [
            'Validar ideas con usuarios reales.',
            'Formar un equipo equilibrado.',
            'Gestionar finanzas con prudencia.',
            'Mantener focus en el producto.'
        ],
        'freelancer': [
            'Diversificar clientes para reducir riesgo.',
            'Establecer tarifas competitivas.',
            'Crear marca personal strong.',
            'Mantener buenos plazos.'
        ]
    }
    return tips.get(career_type, [])


def calculate_career_score(player_state: Dict[str, Any]) -> int:
    score = 0

    skill = player_state.get('skill_level', 0)
    score += skill * 10

    años = player_state.get('años_experiencia', 0)
    score += años * 5

    reputacion = player_state.get('reputacion', 0)
    score += reputacion * 5

    stack_count = len(player_state.get('stack', []))
    score += stack_count * 10

    logros = len(player_state.get('logros', []))
    score += logros * 20

    nivel = player_state.get('nivel', 'trainee')
    nivel_scores = {
        'trainee': 0,
        'junior': 100,
        'semi-senior': 250,
        'senior': 500,
        'lead': 1000
    }
    score += nivel_scores.get(nivel, 0)

    return min(10000, max(0, score))


def get_career_ranking(player_state: Dict[str, Any]) -> Tuple[int, int]:
    score = calculate_career_score(player_state)

    rankings = [
        (0, 999, 'Trainee'),
        (1000, 2499, 'Junior'),
        (2500, 4999, 'Semi-Senior'),
        (5000, 7999, 'Senior'),
        (8000, 10000, 'Lead/CTO')
    ]

    for min_score, max_score, title in rankings:
        if min_score <= score <= max_score:
            return score, min_score

    return score, 10000


def generate_career_summary(player_state: Dict[str, Any]) -> Dict[str, Any]:
    trajectory = get_career_trajectory(player_state)
    score = calculate_career_score(player_state)
    next_milestone = get_next_milestone(player_state)
    advice = generate_career_advice(player_state)
    tips = get_career_tips(trajectory)

    return {
        'trajectory': trajectory,
        'score': score,
        'next_milestone': {
            'name': next_milestone.name if next_milestone else None,
            'skill_required': next_milestone.skill_required if next_milestone else None,
            'progress': get_milestone_progress(player_state, next_milestone) if next_milestone else 100
        } if next_milestone else None,
        'advice': [{'title': a.title, 'description': a.description, 'priority': a.priority} for a in advice[:3]],
        'tips': tips[:2],
        'salary_multiplier': calculate_salary_multiplier(player_state)
    }