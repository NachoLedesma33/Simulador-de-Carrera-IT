from dataclasses import dataclass, field
from typing import List, Dict, Any

LEVELS = ['trainee', 'junior', 'semi-senior', 'senior', 'lead']

LEVEL_SKILL_REQUIREMENTS = {
    'trainee': 0,
    'junior': 25,
    'semi-senior': 50,
    'senior': 75,
    'lead': 90
}

BASE_SALARIES = {
    'trainee': 15000,
    'junior': 30000,
    'semi-senior': 45000,
    'senior': 70000,
    'lead': 100000
}


@dataclass
class Player:
    nivel: str = 'trainee'
    skill_level: int = 0
    salario: int = 15000
    estres: int = 0
    reputacion: int = 0
    stack: List[str] = field(default_factory=list)
    logros: List[str] = field(default_factory=list)
    decisiones_tomadas: List[Dict[str, Any]] = field(default_factory=list)
    años_experiencia: float = 0.0
    nombre: str = ''

    def calculate_career_level(self) -> str:
        if self.skill_level >= LEVEL_SKILL_REQUIREMENTS['lead']:
            return 'lead'
        elif self.skill_level >= LEVEL_SKILL_REQUIREMENTS['senior']:
            return 'senior'
        elif self.skill_level >= LEVEL_SKILL_REQUIREMENTS['semi-senior']:
            return 'semi-senior'
        elif self.skill_level >= LEVEL_SKILL_REQUIREMENTS['junior']:
            return 'junior'
        return 'trainee'

    def is_burned_out(self) -> bool:
        return self.estres > 80

    def can_apply_to_next_level(self) -> bool:
        current_idx = LEVELS.index(self.nivel)
        if current_idx >= len(LEVELS) - 1:
            return False
        next_level = LEVELS[current_idx + 1]
        return self.skill_level >= LEVEL_SKILL_REQUIREMENTS[next_level]

    def get_next_level_skill_required(self) -> int:
        current_idx = LEVELS.index(self.nivel)
        if current_idx >= len(LEVELS) - 1:
            return -1
        next_level = LEVELS[current_idx + 1]
        return LEVEL_SKILL_REQUIREMENTS[next_level]

    def get_skill_gap_to_next_level(self) -> int:
        required = self.get_next_level_skill_required()
        if required == -1:
            return 0
        return max(0, required - self.skill_level)

    def update_nivel(self):
        new_level = self.calculate_career_level()
        if new_level != self.nivel:
            self.nivel = new_level
            self.salario = BASE_SALARIES[new_level]
            return True
        return False

    def add_logro(self, logro: str):
        if logro not in self.logros:
            self.logros.append(logro)

    def add_tecnologia(self, tech: str):
        if tech not in self.stack:
            self.stack.append(tech)

    def add_decision(self, decision: Dict[str, Any]):
        self.decisiones_tomadas.append(decision)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'nombre': self.nombre,
            'nivel': self.nivel,
            'skill_level': self.skill_level,
            'salario': self.salario,
            'estres': self.estres,
            'reputacion': self.reputacion,
            'stack': self.stack,
            'logros': self.logros,
            'decisiones_tomadas': self.decisiones_tomadas,
            'años_experiencia': self.años_experiencia,
            'is_burned_out': self.is_burned_out(),
            'can_apply_to_next_level': self.can_apply_to_next_level(),
            'skill_gap_to_next_level': self.get_skill_gap_to_next_level()
        }
