from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeLocalField, SelectField
from wtforms.validators import DataRequired

class GlossaryForm(FlaskForm):
    term = StringField('Termino', validators=[DataRequired()])
    translation = StringField('Traducción', validators=[DataRequired()])
    description = TextAreaField('Descripción')

class DeleteTermForm(FlaskForm):
    pass  # Este formulario solo necesita el token CSRF


class ChecklistForm(FlaskForm):
    objetive = StringField('Objetivo', validators=[DataRequired()])
    methodology = StringField('Metodología', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    date_target = DateTimeLocalField('Fecha Objetivo', format='%Y-%m-%dT%H:%M')
    status = SelectField('Estado', choices=[
        ('Pendiente', 'Pendiente'), 
        ('En Progreso', 'En Progreso'), 
        ('Completado', 'Completado'), 
        ('En Espera', 'En Espera'), 
        ('Cancelado', 'Cancelado')], default='Pendiente')
    color = StringField('Color', default='#007bff')
    completed = BooleanField('Completada')
    
class DeleteObjetiveForm(FlaskForm):
    pass  # Este formulario solo necesita el token CSRF