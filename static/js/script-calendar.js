document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) {
        console.error('Calendario no encontrado');
        return;
    }

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek', // Cambiar la vista inicial a semana
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale: 'es',
        editable: true, // Permite arrastrar y redimensionar eventos
        droppable: true, // Permite soltar eventos externos
        firstDay: 1, // La semana empieza el lunes
        events: '/task/api/tasks', // Endpoint para cargar eventos

        // Modificar el renderizado de eventos para mostrar la hora y el título
        eventContent: function(arg) {
            let timeText = '';
            if (arg.event.start && arg.event.end) {
                let startTime = arg.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                let endTime = arg.event.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                timeText = startTime + ' - ' + endTime;
            }

            let eventTitle = arg.event.title;

            let innerHtml = `<div class="fc-event-main-wrapper">
                                <div class="fc-event-title">${eventTitle}</div>
                                <div class="fc-event-time">${timeText}</div>
                            </div>`;

            return { html: innerHtml };
        },

        // Callback para manejar clics en eventos
        eventClick: function(info) {
            window.location.href = `/task/edit/${info.event.id}`;
        },

        // Callback para manejar eventos arrastrados
        eventDrop: function(info) {
            const start = info.event.start;
            const end = info.event.end;

            console.log('Event dropped:', {
                id: info.event.id,
                start: start.toISOString(),
                end: end ? end.toISOString() : null,
                view: calendar.view.type
            });

            const data = {
                start: start.toISOString(),
                end: end ? end.toISOString() : null
            };

            console.log('Sending data:', data);

            const csrfToken = getCsrfToken();

            fetch(`/task/api/tasks/${info.event.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(async response => {
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    console.error('Non-JSON response:', await response.text());
                    throw new TypeError("Response was not JSON");
                }
                
                const jsonData = await response.json();
                
                if (!response.ok) {
                    throw new Error(jsonData.message || 'Error updating event');
                }
                
                return jsonData;
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch(error => {
                console.error('Error:', error);
                info.revert();
                alert('Error al actualizar el evento: ' + error.message);
            });
        },

        // Callback para manejar eventos redimensionados
        eventResize: function(info) {
            const start = info.event.start;
            const end = info.event.end;

            console.log('Event resized:', {
                id: info.event.id,
                start: start.toISOString(),
                end: end ? end.toISOString() : null,
                view: calendar.view.type
            });

            const data = {
                start: start.toISOString(),
                end: end ? end.toISOString() : null
            };

            console.log('Sending data:', data);

            const csrfToken = getCsrfToken();

            fetch(`/task/api/tasks/${info.event.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(async response => {
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    console.error('Non-JSON response:', await response.text());
                    throw new TypeError("Response was not JSON");
                }
                
                const jsonData = await response.json();
                
                if (!response.ok) {
                    throw new Error(jsonData.message || 'Error updating event');
                }
                
                return jsonData;
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch(error => {
                console.error('Error:', error);
                info.revert();
                alert('Error al actualizar el evento: ' + error.message);
            });
        },

        // Callback para montar eventos
        eventDidMount: function(info) {
            // Se eliminan los estilos personalizados
        }
    });

    calendar.render();
});

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function deleteTask(taskId) {
    const csrfToken = getCsrfToken();

    fetch(`/task/delete/${taskId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (response.ok) {
            calendar.refetchEvents();
            document.getElementById('taskModal').classList.add('hidden');
        } else {
            alert('Error al eliminar la tarea');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar la tarea');
    });
}