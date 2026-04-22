(function() {
    'use strict';

    const CONFIG = {
        STATS_POLL_INTERVAL: 5000,
        ANIMATION_DURATION: 400,
        KEYBOARD_SHORTCUTS: {
            ENTER: 'Enter',
            ESCAPE: 'Escape',
            ESC: 'Escape'
        }
    };

    const state = {
        isLoading: false,
        currentOptionIndex: 0,
        options: [],
        statsUpdateTimer: null
    };

    document.addEventListener('DOMContentLoaded', function() {
        initTooltips();
        initOptionCards();
        initKeyboardShortcuts();
        initResetConfirmation();
        initStatsPolling();
        initScrollEffects();
        logPageLoad();
        console.log('%c🎮 Simulador de Carrera IT', 'color: #00d9ff; font-size: 16px; font-weight: bold;');
        console.log('%cPresiona ESC para mostrar el menú de opciones', 'color: #a0a0a0;');
    });

    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        console.log('[Init] Tooltips inicializados');
    }

    function initOptionCards() {
        const optionForms = document.querySelectorAll('.option-form');
        state.options = optionForms;

        optionForms.forEach((form, index) => {
            const card = form.querySelector('.option-card');

            card.addEventListener('mouseenter', function() {
                state.currentOptionIndex = index;
                highlightOption(index);
            });

            card.addEventListener('click', function(e) {
                if (!state.isLoading) {
                    showLoadingState();
                    logDecisionChoice(index, form);
                }
            });

            card.addEventListener('keypress', function(e) {
                if (e.key === CONFIG.KEYBOARD_SHORTCUTS.ENTER) {
                    form.querySelector('button').click();
                }
            });
        });

        if (optionForms.length > 0) {
            highlightOption(0);
        }
    }

    function highlightOption(index) {
        state.options.forEach((form, i) => {
            const card = form.querySelector('.option-card');
            if (i === index) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }

    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            if (e.key === CONFIG.KEYBOARD_SHORTCUTS.ESCAPE || e.key === CONFIG.KEYBOARD_SHORTCUTS.ESC) {
                e.preventDefault();
                showEscapeMenu();
                return;
            }

            if (e.key === CONFIG.KEYBOARD_SHORTCUTS.ENTER) {
                const selectedForm = state.options[state.currentOptionIndex];
                if (selectedForm && !state.isLoading) {
                    e.preventDefault();
                    showLoadingState();
                    logDecisionChoice(state.currentOptionIndex, selectedForm);
                    selectedForm.querySelector('button').click();
                }
                return;
            }

            if (e.key === 'ArrowDown' || e.key === 'j') {
                e.preventDefault();
                navigateOptions(1);
                return;
            }

            if (e.key === 'ArrowUp' || e.key === 'k') {
                e.preventDefault();
                navigateOptions(-1);
                return;
            }

            if (e.key >= '1' && e.key <= '9') {
                const num = parseInt(e.key) - 1;
                if (num < state.options.length) {
                    e.preventDefault();
                    state.currentOptionIndex = num;
                    highlightOption(num);
                }
            }
        });

        console.log('[Init] Atajos de teclado inicializados');
    }

    function navigateOptions(direction) {
        const newIndex = state.currentOptionIndex + direction;
        if (newIndex >= 0 && newIndex < state.options.length) {
            state.currentOptionIndex = newIndex;
            highlightOption(newIndex);

            const selectedCard = state.options[newIndex].querySelector('.option-card');
            selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function showEscapeMenu() {
        const menuHtml = `
            <div class="modal fade" id="escapeMenuModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content" style="background: var(--bg-card); border: 1px solid var(--border-color);">
                        <div class="modal-header" style="border-bottom: 1px solid var(--border-color);">
                            <h5 class="modal-title" style="color: var(--text-primary);">Menú de Opciones</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="d-grid gap-2">
                                <a href="/" class="btn btn-outline-light"><i class="ph-bold ph-house" style="margin-right: 6px;"></i> Ir al Inicio</a>
                                <a href="/stats" class="btn btn-outline-light"><i class="ph-bold ph-chart-bar" style="margin-right: 6px;"></i> Ver Estadísticas</a>
                                <button onclick="window.location.reload()" class="btn btn-outline-light"><i class="ph-bold ph-arrows-clockwise" style="margin-right: 6px;"></i> Recargar Página</button>
                                <hr style="border-color: var(--border-color);">
                                <a href="/reset" class="btn btn-danger"><i class="ph-bold ph-trash" style="margin-right: 6px;"></i> Reiniciar Partida</a>
                            </div>
                        </div>
                        <div class="modal-footer" style="border-top: 1px solid var(--border-color);">
                            <small class="text-muted">Presiona ESC para cerrar</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const existingModal = document.getElementById('escapeMenuModal');
        if (existingModal) {
            existingModal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', menuHtml);
        const modal = new bootstrap.Modal(document.getElementById('escapeMenuModal'));
        modal.show();

        document.getElementById('escapeMenuModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    function initResetConfirmation() {
        const resetLinks = document.querySelectorAll('a[href="/reset"]');
        const resetButtons = document.querySelectorAll('button[type="submit"]');

        resetButtons.forEach(button => {
            if (button.textContent.toLowerCase().includes('reiniciar')) {
                button.addEventListener('click', function(e) {
                    const form = button.closest('form');
                    if (form && form.action && form.action.includes('decision_submit')) {
                        return;
                    }

                    if (!confirm('¿Estás seguro de que quieres reiniciar la partida? Perderás todo el progreso.')) {
                        e.preventDefault();
                        return false;
                    }
                });
            }
        });

        resetLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                if (!confirm('¿Estás seguro de que quieres reiniciar la partida? Perderás todo el progreso.')) {
                    e.preventDefault();
                    return false;
                }
                console.log('[Game] Partida reiniciada por el usuario');
            });
        });
    }

    function initStatsPolling() {
        const statsPanel = document.getElementById('statsPanel');
        if (!statsPanel) {
            return;
        }

        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.warn('[Stats] Error:', data.error);
                        return;
                    }
                    updateStatsUI(data);
                })
                .catch(error => {
                    console.error('[Stats] Error de conexión:', error);
                });
        }

        state.statsUpdateTimer = setInterval(updateStats, CONFIG.STATS_POLL_INTERVAL);
        console.log('[Init] Polling de stats iniciado (cada ' + (CONFIG.STATS_POLL_INTERVAL / 1000) + 's)');
    }

    function updateStatsUI(data) {
        const elements = {
            skill: document.getElementById('playerSkill'),
            skillBar: document.getElementById('skillBar'),
            stress: document.getElementById('playerStress'),
            stressBar: document.getElementById('stressBar'),
            reputation: document.getElementById('playerRep'),
            salary: document.getElementById('playerSalary'),
            level: document.getElementById('playerLevel')
        };

        if (elements.skill) {
            elements.skill.textContent = data.skill_level;
            if (elements.skillBar) {
                elements.skillBar.style.width = data.skill_level + '%';
                elements.skillBar.className = 'progress-bar ' + getSkillColor(data.skill_level);
            }
        }

        if (elements.stress) {
            elements.stress.textContent = data.estres + '%';
            elements.stress.className = 'stat-value' + (data.estres > 70 ? ' text-danger' : '');
            if (elements.stressBar) {
                elements.stressBar.style.width = data.estres + '%';
                elements.stressBar.className = 'progress-bar ' + getStressColor(data.estres);
            }
        }

        if (elements.reputation) {
            elements.reputation.textContent = data.reputacion;
        }

        if (elements.salary) {
            elements.salary.textContent = '$' + data.salario.toLocaleString();
        }

        if (elements.level) {
            elements.level.textContent = data.nivel.charAt(0).toUpperCase() + data.nivel.slice(1);
        }

        if (data.estres > 80) {
            showBurnoutWarning();
        }
    }

    function getSkillColor(value) {
        if (value >= 70) return 'bg-success';
        if (value >= 40) return 'bg-warning';
        return 'bg-danger';
    }

    function getStressColor(value) {
        if (value < 30) return 'bg-success';
        if (value <= 70) return 'bg-warning';
        return 'bg-danger';
    }

    function showBurnoutWarning() {
        const existing = document.querySelector('.alert-burnout');
        if (existing) return;

        const alert = document.createElement('div');
        alert.className = 'alert-burnout';
        alert.innerHTML = '⚠️ <strong>¡Alto nivel de estrés!</strong> - Riesgo de burnout.';

        const container = document.querySelector('.main-content') || document.querySelector('.flash-messages');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            console.warn('[Game] Alerta de burnout mostrada');
        }
    }

    function initScrollEffects() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-visible');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.option-card, .stat-card, .decision-card').forEach(el => {
            observer.observe(el);
        });

        console.log('[Init] Efectos de scroll inicializados');
    }

    function showLoadingState() {
        state.isLoading = true;
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 text-light">Procesando decisión...</p>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(15, 15, 26, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                animation: fadeIn 0.2s ease;
            }
            .loading-spinner {
                text-align: center;
            }
            .spinner-border {
                width: 3rem;
                height: 3rem;
                border-width: 0.25rem;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(overlay);
    }

    function hideLoadingState() {
        state.isLoading = false;
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 200);
        }
    }

    function logPageLoad() {
        console.group('[Page] Información de carga');
        console.log('URL:', window.location.href);
        console.log('User Agent:', navigator.userAgent);
        console.log('Viewport:', window.innerWidth + 'x' + window.innerHeight);
        console.log('Fecha:', new Date().toISOString());
        console.groupEnd();
    }

    function logDecisionChoice(index, form) {
        const optionLabel = form.querySelector('.option-label')?.textContent || 'Opción ' + (index + 1);
        const decisionTitle = document.querySelector('.decision-title')?.textContent || 'Unknown';
        const playerLevel = document.getElementById('playerLevelValue')?.textContent || 'N/A';

        console.group('%c🎯 Decisión tomada', 'color: #00ff96; font-weight: bold;');
        console.log('Decisión:', decisionTitle);
        console.log('Opción elegida:', optionLabel);
        console.log('Índice:', index);
        console.log('Nivel actual:', playerLevel);
        console.log('Timestamp:', new Date().toISOString());
        console.groupEnd();

        const stats = {
            event: 'decision_made',
            decision: decisionTitle,
            option: optionLabel,
            index: index,
            timestamp: new Date().toISOString()
        };

        if (typeof gtag !== 'undefined') {
            gtag('event', 'decision_made', stats);
        }
    }

    // Removed beforeunload event listener that interfered with form submission

    window.SimuladorIT = {
        showLoading: showLoadingState,
        hideLoading: hideLoadingState,
        navigateOptions: navigateOptions,
        refreshStats: function() {
            fetch('/api/stats').then(r => r.json()).then(updateStatsUI);
        },
        getState: function() {
            return { ...state };
        }
    };

})();
