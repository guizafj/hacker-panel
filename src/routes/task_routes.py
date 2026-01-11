from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from html_sanitizer import Sanitizer
from dateutil.parser import isoparse
from datetime import timedelta

from extensions import db
from src.models.task import Task
from src.forms.task_form import TaskForm

# Creación del Blueprint para la task
task_bp = Blueprint("task", __name__)
sanitizer = Sanitizer()


@task_bp.route("/add", methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        current_app.logger.info("Formulario validado correctamente.")
        try:
            task = Task(
                title=form.title.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                type=form.type.data,
                color=form.color.data,
                completed=form.completed.data,
                recurring=form.recurring.data,
                days_of_week=",".join(form.days_of_week.data)
                if form.days_of_week.data
                else "",
                start_recur=form.start_recur.data,
                end_recur=form.end_recur.data,
            )
            db.session.add(task)
            db.session.commit()
            current_app.logger.info(f"Tarea creada exitosamente: {task}")
            flash("Tarea creada exitosamente", "success")
            return redirect(url_for("generales.index"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear la tarea: {e}", exc_info=True)
            flash("Error al crear la tarea.", "error")
            return render_template("add_task.html", form=form)
    else:
        current_app.logger.info("El formulario no es valido")
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.error(f"Error en el campo {field}: {error}")
    return render_template("add_task.html", form=form)


@task_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.start_date = form.start_date.data
        task.end_date = form.end_date.data
        task.type = form.type.data
        task.color = form.color.data
        task.completed = form.completed.data
        task.recurring = form.recurring.data
        task.days_of_week = (
            ",".join(form.days_of_week.data) if form.days_of_week.data else ""
        )
        task.start_recur = form.start_recur.data
        task.end_recur = form.end_recur.data

        current_app.logger.info(
            f"Task ID: {task_id}, Recurring: {task.recurring}, Days of Week: {task.days_of_week}, Start Recur: {task.start_recur}, End Recur: {task.end_recur}"
        )  # Add this line

        db.session.commit()
        flash("Tarea actualizada exitosamente!", "success")
        return redirect(url_for("generales.index"))

    return render_template("edit_task.html", form=form, task=task)


@task_bp.route("/toggle_complete/<int:task_id>", methods=["POST"])
def toggle_complete(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm()
    if form.validate_on_submit():
        task.completed = not task.completed
        db.session.commit()
        flash("Estado de la tarea actualizado.", "success")
        return redirect(url_for("generales.index"))
    flash("Error al actualizar el estado de la tarea. Token CSRF inválido.", "danger")
    return redirect(url_for("generales.index"))


@task_bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Tarea eliminada.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar la tarea.", "error")
        current_app.logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
    return redirect(url_for("generales.index"))


# --- API para el Calendario ---
@task_bp.route("/api/tasks")
def api_tasks():
    tasks = Task.query.all()
    events = []
    for task in tasks:
        try:
            if task.recurring:
                start_date = task.start_recur or task.start_date
                end_date = task.end_recur

                if task.days_of_week:  # Verificar si days_of_week no está vacío
                    days_of_week = [int(d) for d in task.days_of_week.split(",")]
                else:
                    days_of_week = []  # Asignar una lista vacía si days_of_week está vacío

                print(
                    f"Task ID: {task.id}, Start Date: {start_date}, End Date: {end_date}, Days of Week: {days_of_week}"
                )

                if start_date and end_date and days_of_week:
                    # Validar que start_date y end_date no sean None
                    if task.start_date and task.end_date:
                        duration = task.end_date - task.start_date
                    else:
                        print(
                            f"Error procesando la tarea {task.id}: start_date o end_date es None"
                        )
                        continue

                    current_date = start_date
                    while current_date <= end_date:
                        print(
                            f"Current Date: {current_date}, Weekday: {current_date.weekday()}"
                        )
                        if current_date.weekday() in days_of_week:
                            # Calcular la fecha de finalización del evento recurrente
                            event_end = current_date + duration

                            event = {
                                "id": task.id,
                                "title": task.title,
                                "start": current_date.isoformat(),
                                "end": event_end.isoformat(),
                                "allDay": False,
                                "backgroundColor": task.color,
                                "borderColor": task.color,
                                "textColor": "#ffffff",
                                "extendedProps": {
                                    "description": task.description or "",
                                    "completed": task.completed,
                                },
                            }
                            events.append(event)
                            print(f"Evento recurrente generado: {event}")
                        current_date += timedelta(days=1)
            else:
                # Evento no recurrente
                if task.start_date and task.end_date:
                    event = {
                        "id": task.id,
                        "title": task.title,
                        "start": task.start_date.isoformat(),
                        "end": task.end_date.isoformat(),
                        "allDay": False,
                        "backgroundColor": task.color,
                        "borderColor": task.color,
                        "textColor": "#ffffff",
                        "extendedProps": {
                            "description": task.description or "",
                            "completed": task.completed,
                            "originalStart": task.start_date.isoformat()
                            if task.start_date
                            else None,
                            "originalEnd": task.end_date.isoformat()
                            if task.end_date
                            else None,
                        },
                    }
                    events.append(event)
        except Exception as e:
            print(f"Error procesando la tarea {task.id}: {e}")
    return jsonify(events)


@task_bp.route("/api/tasks/pending")
def api_pending_tasks():
    tasks = Task.query.filter_by(completed=False).order_by(Task.start_date).all()
    return jsonify([task.to_dict() for task in tasks])


@task_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        # Verify JSON content type
        if not request.is_json:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Content-Type must be application/json",
                    }
                ),
                400,
                {"Content-Type": "application/json"},
            )

        data = request.get_json()

        # Log received data
        current_app.logger.info(f"Received data for task {task_id}: {data}")

        task = Task.query.get_or_404(task_id)

        # Update dates with validation
        if "start" in data:
            try:
                task.start_date = isoparse(data["start"])
            except Exception as e:
                return (
                    jsonify(
                        {"status": "error", "message": f"Invalid start date: {str(e)}"}
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )

        if "end" in data:
            try:
                task.end_date = isoparse(data["end"]) if data["end"] else None
            except Exception as e:
                return (
                    jsonify(
                        {"status": "error", "message": f"Invalid end date: {str(e)}"}
                    ),
                    400,
                    {"Content-Type": "application/json"},
                )

        db.session.commit()

        # Return success response
        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "id": task.id,
                        "start": task.start_date.isoformat()
                        if task.start_date
                        else None,
                        "end": task.end_date.isoformat() if task.end_date else None,
                    },
                }
            ),
            200,
            {"Content-Type": "application/json"},
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error updating task {task_id}: {str(e)}", exc_info=True
        )
        return (
            jsonify({"status": "error", "message": str(e)}),
            400,
            {"Content-Type": "application/json"},
        )


@task_bp.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify(task.to_dict())
