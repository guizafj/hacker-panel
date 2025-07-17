from flask import Blueprint, render_template
from src.forms.task_form import TaskForm
from src.models.task import Task

general_bp = Blueprint('generales', __name__)


@general_bp.route('/')
def index():
    # Obtener todas las tareas, ordenadas por fecha de inicio
    tasks = Task.query.order_by(
        Task.start_date.asc().nulls_last(), 
        Task.completed.asc()
    ).all()
    
    # Crear el formulario para el modal
    form = TaskForm()
    
    return render_template(
        'index.html',
        tasks=tasks,  # Pasar las tareas al template
        form=form
    )

