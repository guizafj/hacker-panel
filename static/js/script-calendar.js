/**
 * script-calendar.js — Hacker Panel
 *
 * Funcionalidades implementadas:
 *  - Vista mes por defecto (dayGridMonth)
 *  - Drag & Drop con feedback visual
 *  - Selectable dates → redirige a /task/add con fechas pre-rellenadas
 *  - Background Events (bloques de estudio fijos)
 *  - Modal de detalle responsive y siempre dentro del viewport
 *  - toggleTask / deleteTask con calendar.refetchEvents() (fix scope)
 *  - updateTaskDates() única función para eventDrop y eventResize
 */

// Scope de módulo: accesible desde todas las funciones auxiliares
let calendar = null;

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function formatDateRange(start, end) {
    if (!start) return '';
    const dateOpts = { weekday: 'long', day: 'numeric', month: 'long' };
    const timeOpts = { hour: '2-digit', minute: '2-digit' };
    const dateStr  = start.toLocaleDateString('es-ES', dateOpts);
    const startT   = start.toLocaleTimeString('es-ES', timeOpts);
    if (!end) return `${dateStr}, ${startT}`;
    const endT = end.toLocaleTimeString('es-ES', timeOpts);
    return `${dateStr}  ·  ${startT} – ${endT}`;
}

// ─────────────────────────────────────────────
// Actualizar fechas (drag & drop / resize)
// ─────────────────────────────────────────────

function updateTaskDates(info) {
    const start = info.event.start;
    const end   = info.event.end;

    fetch(`/task/api/tasks/${info.event.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Accept':       'application/json',
            'X-CSRFToken':  getCsrfToken()
        },
        body: JSON.stringify({
            start: start.toISOString(),
            end:   end ? end.toISOString() : null
        })
    })
    .then(async response => {
        const ct = response.headers.get('content-type') || '';
        if (!ct.includes('application/json')) {
            throw new TypeError('Respuesta no JSON: ' + await response.text());
        }
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Error al actualizar');
    })
    .catch(error => {
        console.error('Error al mover/redimensionar evento:', error);
        info.revert();
        alert('No se pudo actualizar la tarea: ' + error.message);
    });
}

// ─────────────────────────────────────────────
// Modal de detalle
// ─────────────────────────────────────────────

function openTaskModal(info) {
    const event     = info.event;
    const props     = event.extendedProps || {};
    const completed = !!props.completed;

    // No abrir modal para background events
    if (event.display === 'background') return;

    document.getElementById('taskModalTitle').textContent = event.title;

    // Descripción
    const descWrapper = document.getElementById('taskModalDescWrapper');
    const descEl      = document.getElementById('taskModalDesc');
    if (props.description && props.description.trim()) {
        descEl.textContent = props.description;
        descWrapper.classList.remove('hidden');
    } else {
        descWrapper.classList.add('hidden');
    }

    // Fechas
    document.getElementById('taskModalDates').textContent =
        formatDateRange(event.start, event.end);

    // Estado
    const statusEl = document.getElementById('taskModalStatus');
    if (completed) {
        statusEl.textContent = '✓ Completada';
        statusEl.className   = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    } else {
        statusEl.textContent = '● Pendiente';
        statusEl.className   = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    }

    // Botón toggle
    const toggleBtn = document.getElementById('taskModalToggle');
    toggleBtn.textContent = completed ? 'Marcar pendiente' : 'Marcar completada';
    toggleBtn.onclick = () => toggleTask(event.id);

    document.getElementById('taskModalEdit').href      = `/task/edit/${event.id}`;
    document.getElementById('taskModalDelete').onclick = () => deleteTask(event.id);

    // Mostrar modal centrado en viewport
    const modal = document.getElementById('taskModal');
    modal.classList.remove('hidden');
    requestAnimationFrame(() => {
        document.getElementById('taskModalClose').focus();
    });
}

function closeTaskModal() {
    document.getElementById('taskModal').classList.add('hidden');
}

// ─────────────────────────────────────────────
// Eliminar tarea
// ─────────────────────────────────────────────

function deleteTask(taskId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) return;

    fetch(`/task/delete/${taskId}`, {
        method:  'POST',
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error al eliminar');
        closeTaskModal();
        if (calendar) calendar.refetchEvents();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('No se pudo eliminar la tarea: ' + error.message);
    });
}

// ─────────────────────────────────────────────
// Marcar completada / pendiente
// ─────────────────────────────────────────────

function toggleTask(taskId) {
    fetch(`/task/toggle/${taskId}`, {
        method:  'POST',
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error al actualizar estado');
        closeTaskModal();
        if (calendar) calendar.refetchEvents();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('No se pudo actualizar el estado: ' + error.message);
    });
}

// ─────────────────────────────────────────────
// Background events (bloques de estudio fijos)
// Estos son estáticos y se definen aquí.
// Cuando tengas el modelo de "recursos" listo,
// puedes moverlos a un endpoint de la API.
// ─────────────────────────────────────────────

const STUDY_BLOCKS = [
    {
        title:      'Bloque de estudio',
        daysOfWeek: [1, 2, 3, 4, 5],   // lun–vie
        startTime:  '09:00',
        endTime:    '11:00',
        display:    'background',
        color:      '#3b82f6',          // blue-500
        classNames: ['fc-bg-event']
    },
    {
        title:      'Repaso',
        daysOfWeek: [1, 3, 5],          // lun, mié, vie
        startTime:  '21:00',
        endTime:    '22:30',
        display:    'background',
        color:      '#8b5cf6',          // violet-500
        classNames: ['fc-bg-event']
    }
];

// ─────────────────────────────────────────────
// Inicialización
// ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    calendar = new FullCalendar.Calendar(calendarEl, {

        // ── Vista y apariencia ─────────────────────────────────
        initialView:  'dayGridMonth',       // Vista mes por defecto
        headerToolbar: {
            left:   'prev,next today',
            center: 'title',
            right:  'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale:       'es',
        firstDay:     1,                    // Semana empieza el lunes
        nowIndicator: true,                 // Línea roja en hora actual
        height:       'auto',               // Sin scroll interno

        // ── Interactividad ─────────────────────────────────────
        editable:     true,                 // Drag & drop + resize
        droppable:    true,
        selectable:   true,                 // Selección de rango de fechas
        selectMirror: true,                 // Preview al seleccionar

        // ── Fuentes de eventos ─────────────────────────────────
        eventSources: [
            {
                url:     '/task/api/tasks',
                failure: function () {
                    console.error('Error al cargar las tareas del calendario');
                }
            },
            STUDY_BLOCKS
        ],

        // Máximo de eventos visibles por día en vista mes
        dayMaxEvents: 3,

        // ── Renderizado de eventos ─────────────────────────────
        eventContent: function (arg) {
            if (arg.event.display === 'background') return;

            const event     = arg.event;
            const completed = !!((event.extendedProps || {}).completed);

            let timeText = '';
            if (event.start && event.end) {
                const s = event.start.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                const e = event.end.toLocaleTimeString('es-ES',   { hour: '2-digit', minute: '2-digit' });
                timeText = `${s}–${e}`;
            }

            const titleStyle = completed
                ? 'text-decoration:line-through;opacity:0.65;'
                : '';

            return {
                html: `<div style="padding:2px 4px;overflow:hidden;">
                           <div style="font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;${titleStyle}">
                               ${event.title}
                           </div>
                           ${timeText ? `<div style="font-size:0.7em;opacity:0.85;">${timeText}</div>` : ''}
                       </div>`
            };
        },

        // ── Clic en evento → modal ─────────────────────────────
        eventClick: function (info) {
            info.jsEvent.preventDefault();
            openTaskModal(info);
        },

        // ── Selección de rango → nueva tarea ──────────────────
        select: function (info) {
            // Redirige al form con fechas pre-rellenadas vía query params.
            // En add_task.html, leer con: new URLSearchParams(window.location.search)
            const start = info.startStr.slice(0, 16);
            const end   = info.endStr ? info.endStr.slice(0, 16) : start;
            window.location.href = `/task/add?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
        },

        // ── Drag & drop ────────────────────────────────────────
        eventDrop:   updateTaskDates,
        eventResize: updateTaskDates,

        // Feedback visual al arrastrar
        eventDragStart: function (info) { info.el.style.opacity = '0.55'; },
        eventDragStop:  function (info) { info.el.style.opacity = ''; },
    });

    calendar.render();

    // ── Modal: cerrar con X, backdrop o Escape ─────────────────
    document.getElementById('taskModalClose').addEventListener('click', closeTaskModal);

    document.getElementById('taskModal').addEventListener('click', function (e) {
        if (e.target === this) closeTaskModal();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeTaskModal();
    });
});