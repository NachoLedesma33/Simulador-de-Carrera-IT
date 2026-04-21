# Simulador de Carrera IT

![Estado](https://img.shields.io/badge/Estado-Activo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-blue)
![Licencia](https://img.shields.io/badge/Licencia-MIT-lightgrey)

Un simulador interactivo y no lineal de carrera en tecnología. Toma decisiones, desarrolla habilidades, gestiona el estrés y alcanza la cima: de Trainee a CTO.

## 🎮 Demo Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/simulador-carrera-it.git
cd simulador-carrera-it

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
```

Abre http://localhost:5000 en tu navegador.

## 🏗️ Arquitectura

```
simulador-carrera-it/
├── app.py                 # Aplicación Flask principal
├── config.py             # Configuración (SECRET_KEY, sesiones)
├── models/
│   ├── player.py          # Modelo del jugador
│   └── decision_engine.py # Motor de decisiones
├── services/
│   ├── effect_applier.py      # Aplicador de efectos
│   ├── session_manager.py       # Gestión de sesiones
│   ├── event_system.py       # Sistema de eventos
│   └── achievement_system.py # Sistema de logros
├── utils/
│   ├── validators.py        # Validaciones
│   └── career_paths.py       # Caminos de carrera
├── data/
│   ├── decisions.yaml    # Árbol de decisiones
│   ├── events.yaml     # Eventos aleatorios
│   └── achievements.yaml # Logros
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── decision.html
│   └── partials/     # Componentes reutilizables
├── static/
│   ├── css/style.css
│   └── js/main.js
└── tests/
    └── test_engine.py
```

### Flujo de Datos

```
Jugador → Decisión → Efectos → Stats → Logros/Eventos
   ↑                    ↓
 Sesión ←─────────── Guardado
```

## 🎯 Estructura de Decisiones

Cada nodo de decisión en `decisions.yaml` tiene:

```yaml
nombre_decision:
  id: nombre_decision
  titulo: "Título Visible"
  descripcion: "Contexto de la decisión"
  tipo: inicio|eleccion_carrera|aprender|proyecto|desafio|promocion|riesgo
  opciones:
    - label: "Opción 1"
      efectos:
        - stat: skill_level
          delta: 10
        - stat: estres
          delta: 15
        - add: React
      next_node: siguiente_decision
      requiere: null
    - label: "Opción 2"
      efectos:
        - stat: salario
          delta: -5000
      next_node: otra_decision
      requiere:
        skill_min: 40
```

### Tipos de Nodos

| Tipo | Descripción |
|------|-------------|
| `inicio` | Punto de partida |
| `eleccion_carrera` | Elección de especialización |
| `aprender` | Oportunidad de estudio |
| `proyecto` | Proyecto especial |
| `desafio` | Desafío técnico |
| `promocion` | Subida de nivel |
| `riesgo` | Decisión de alto riesgo |

## 📊 Features Principales

### Sistema de Stats

- **Skill Level** (0-100): Habilidades técnicas
- **Estrés** (0-100): Puede llevar a burnout
- **Reputación** (0-100): Reconocimiento en la industria
- **Salario** (0-50000): Remuneración actual
- **Stack**: Tecnologías dominadas
- **Logros**: Hitos desbloqueados

### Motor de Efectos

```python
# Los efectos pueden:
apply_stat_change(state, 'skill_level', +10)    # Sumar/restar
apply_add_tech(state, 'React')                     # Agregar tecnología
apply_add_achievement(state, 'First Win')           # Desbloquear logro
apply_set_flag(state, 'has_certification', True)     # Variable booleana
```

### Eventos Aleatorios

Probabilidad configurable en `events.yaml`. Ejemplos:

- **Positivos**: Oferta inesperada (+30% salario), Mentor encontrado (+20 skill)
- **Negativos**: Bug en producción (-10 reputación), Deadline ajustado (+15 estrés)
- **Neutrales**: Cambio de gerente, Invitación a conferencia

### Sistema de Logros

Logros desbloqueables con condiciones:

| Logro | Condición | Puntos |
|-------|-----------|--------|
| Stack Master | 5+ tecnologías | 50 |
| Full Stack Hero | Frontend + Backend + DB | 100 |
| Networking King | Reputación > 90 | 100 |
| Senior Velocity | Senior en <5 años | 150 |
| Resiliente | Estrés >80 sin burnout | 100 |

### Caminos de Carrera

El juego detecta automáticamente tu perfil:

- **Especialista**: Skill alto, stack especializado
- **Manager**: Decisiones de liderazgo
- **Emprendedor**: Startup o freelance
- **Freelancer**: work-from-anywhere

## 🎨 Capturas de Pantalla

### Pantalla de Inicio
```
┌─────────────────────────────────────┐
│      💻 Simulador de Carrera IT       │
│                                     │
│   Construye tu trayectoria en        │
│      tecnología                     │
│                                     │
│   Características:                   │
│   • Decisiones que moldan carrera │
│   • Desarrolla habilidades          │
│   • Elige: startup o empresa      │
│   • Enfrenta eventos inesperados │
│   • Alcanza la cima: CTO          │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ ¿Cómo te llamas?           │  │
│   │ [_______________]          │  │
│   │  [Comenzar Carrera]        │  │
│   └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Decisión en Curso
```
┌──────────────────────────────────────────┐
│ 📊 Estadísticas        🛠️ Tech Stack    │
│ Nivel: Junior           [React] [Python] │
│ Skill: 45 ████████░░░░  [SQL]           │
│ Estrés: 30 ███░░░░░░░░                   │
│ Salario: $35,000                        │
├──────────────────────────────────────────┤
│                                          │
│   📚 Tu primera entrevista técnica       │
│                                          │
│   Has conseguido una entrevista en una   │
│   startup local. Te preguntan sobre     │
│   tus intereses.                          │
│                                          │
│   ┌────────────────────────────────────┐  │
│   │ 1. Me interesa más el frontend  → │  │
│   └────────────────────────────────────┘  │
│   ┌────────────────────────────────────┐  │
│   │ 2. Prefiero el desarrollo backend → │  │
│   └────────────────────────────────────┘  │
│   ┌────────────────────────────────────┐  │
│   │ 3. Me atraen los datos y analytics →│  │
│   └────────────────────────────────────┘  │
│                                          │
│   [Ver Stats] [Reiniciar]               │
└──────────────────────────────────────────┘
```

## 🚀 Guía de Desarrollo

### Agregar Nueva Decisión

1. Editar `data/decisions.yaml`:

```yaml
mi_decision:
  id: mi_decision
  titulo: "Mi nueva decisión"
  descripcion: "Descripción del escenario"
  tipo: aprender
  opciones:
    - label: "Estudiar nueva tecnología"
      efectos:
        - stat: skill_level
          delta: 15
        - add: NuevaTech
      next_node: siguiente
      requiere:
        skill_min: 30
```

2. Reiniciar el servidor

### Agregar Nuevo Evento

1. Editar `data/events.yaml`:

```yaml
mi_evento:
  id: mi_evento
  titulo: "¡Oferta especial!"
  descripcion: "Te llega una oferta inesperada"
  tipo: positivo
  probabilidad: 0.10
  efectos:
    - stat: salario
      delta: 10000
  requerimientos:
    skill_min: 50
  mensaje: "¡Tu reputación te precede!"
```

### Agregar Nuevo Logro

1. Editar `data/achievements.yaml` con la estructura del ejemplo existente
2. Implementar condición en `services/achievement_system.py`

## 🧪 Testing

```bash
# Instalar pytest
pip install pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests específicos
pytest tests/test_engine.py::TestEffectApplier -v
```

## 📈 Roadmap

### Fase 1 - MVP (Completado ✅)
- [x] Configuración base Flask
- [x] Modelo de jugador
- [x] Árbol de decisiones YAML
- [x] Motor de efectos
- [x] Eventos aleatorios
- [x] Sistema de logros
- [x] Interfaz web básica

### Fase 2 - Enhancements (En Progreso)
- [ ] Guardado múltiple de partidas
- [ ] Exportar historia a PDF/JSON
- [ ] Modo competitivo (leaderboard)
- [ ] Historial de decisiones visual
- [ ] Animaciones CSS avanzadas

### Fase 3 - Features Futuras
- [ ] Integración con API de薪资 (Salary) reales
- [ ] Conexión a LinkedIn para logros reales
- [ ] Modo multiplayer local
- [ ] Challenges diarios
- [ ] Certificaciones verificables
- [ ] Podcast/Video de decisiones destacadas

## 🤝 Contribuir

1. Fork el repositorio
2. Crear branch (`git checkout -b feature/nueva-feature`)
3. Commit cambios (`git commit -m 'Agrega nueva feature'`)
4. Push al branch (`git push origin feature/nueva-feature`)
5. Crear Pull Request

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

## 🙏 Créditos

Desarrollado con 💙 usando Flask, Jinja2, Bootstrap 5 y mucho café.

---

**¡Buena suerte en tu carrera en IT!** 🚀