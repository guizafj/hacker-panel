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

task_bp = Blueprint("task", __name__)
sanitizer = Sanitizer()


@task_bp.route("/add", methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
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
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.warning(f"Error de validación en '{field}': {error}")
    return render_template("add_task.html", form=form)


@task_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    # FIX: .query.get_or_404() está deprecado en SQLAlchemy 2.x.
    # Se usa db.session.get() + abort manual, patrón recomendado.
    task = db.session.get(Task, task_id)
    if task is None:
        from flask import abort
        abort(404)

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
            f"Task ID: {task_id}, Recurring: {task.recurring}, "
            f"Days of Week: {task.days_of_week}, "
            f"Start Recur: {task.start_recur}, End Recur: {task.end_recur}"
        )

        db.session.commit()
        flash("Tarea actualizada exitosamente!", "success")
        return redirect(url_for("generales.index"))

    return render_template("edit_task.html", form=form, task=task)


@task_bp.route("/toggle_complete/<int:task_id>", methods=["POST"])
def toggle_complete(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        from flask import abort
        abort(404)

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
    task = db.session.get(Task, task_id)
    if task is None:
        from flask import abort
        abort(404)

    try:
        db.session.delete(task)
        db.session.commit()
        flash("Tarea eliminada.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar la tarea.", "error")
        current_app.logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
    return redirect(url_for("generales.index"))


@task_bp.route("/api/tasks")
def api_tasks():
    tasks = Task.query.all()
    events = []

    for task in tasks:
        try:
            if task.recurring:
                start_date = task.start_recur or task.start_date
                end_date = task.end_recur

                # FIX: reemplazados todos los print() por current_app.logger
                if task.days_of_week:
                    days_of_week = [int(d) for d in task.days_of_week.split(",")]
                else:
                    days_of_week = []

                current_app.logger.debug(
                    f"Task ID: {task.id}, Start: {start_date}, End: {end_date}, "
                    f"Days of Week: {days_of_week}"
                )

                if start_date and end_date and days_of_week:
                    if not (task.start_date and task.end_date):
                        current_app.logger.warning(
                            f"Tarea {task.id}: start_date o end_date es None, omitiendo"
                        )
                        continue

                    duration = task.end_date - task.start_date
                    current_date = start_date

                    while current_date <= end_date:
                        if current_date.weekday() in days_of_week:
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
                        current_date += timedelta(days=1)
            else:
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
                            "originalStart": task.start_date.isoformat(),
                            "originalEnd": task.end_date.isoformat(),
                        },
                    }
                    events.append(event)
        except Exception as e:
            current_app.logger.error(
                f"Error procesando la tarea {task.id}: {e}", exc_info=True
            )

    return jsonify(events)


@task_bp.route("/api/tasks/pending")
def api_pending_tasks():
    tasks = Task.query.filter_by(completed=False).order_by(Task.start_date).all()
    return jsonify([task.to_dict() for task in tasks])


@task_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400

        data = request.get_json()
        current_app.logger.info(f"Received data for task {task_id}: {data}")

        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"status": "error", "message": "Tarea no encontrada"}), 404

        if "start" in data:
            try:
                task.start_date = isoparse(data["start"])
            except Exception as e:
                return jsonify({"status": "error", "message": f"Invalid start date: {str(e)}"}), 400

        if "end" in data:
            try:
                task.end_date = isoparse(data["end"]) if data["end"] else None
            except Exception as e:
                return jsonify({"status": "error", "message": f"Invalid end date: {str(e)}"}), 400

        db.session.commit()

        return jsonify({
            "status": "success",
            "data": {
                "id": task.id,
                "start": task.start_date.isoformat() if task.start_date else None,
                "end": task.end_date.isoformat() if task.end_date else None,
            },
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 400


@task_bp.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        from flask import abort
        abort(404)

    task.completed = not task.completed
    db.session.commit()
    return jsonify(task.to_dict())