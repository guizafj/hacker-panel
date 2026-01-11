from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    ValidationError,
)
from wtforms.validators import DataRequired
from src.models.glossary import Term


class GlossaryForm(FlaskForm):
    term = StringField("Termino", validators=[DataRequired()])
    translation = StringField("Traducción", validators=[DataRequired()])
    description = TextAreaField("Descripción")

    def validate_term(self, field):
        """
        Valida que el termino no exista en la base de datos y que no este vacio

        Args:
            term (Field): Campo term del formulario

        Raises:
            ValidationError: Si el term es invalido  o ya existe
        """
        try:
            Term.validar_term(field.data, term_id=None)
        except ValueError as e:
            raise ValidationError(str(e))


class DeleteTermForm(FlaskForm):
    pass  # Este formulario solo necesita el token CSRF


class ChecklistForm(FlaskForm):
    objetive = StringField("Objetivo", validators=[DataRequired()])
    methodology = StringField("Metodología", validators=[DataRequired()])
    description = TextAreaField("Descripción")
    date_target = DateTimeLocalField("Fecha Objetivo", format="%Y-%m-%dT%H:%M")
    status = SelectField(
        "Estado",
        choices=[
            ("Pendiente", "Pendiente"),
            ("En Progreso", "En Progreso"),
            ("Completado", "Completado"),
            ("En Espera", "En Espera"),
            ("Cancelado", "Cancelado"),
        ],
        default="Pendiente",
    )
    color = StringField("Color", default="#007bff")
    completed = BooleanField("Completada")


class DeleteObjetiveForm(FlaskForm):
    pass  # Este formulario solo necesita el token CSRF
