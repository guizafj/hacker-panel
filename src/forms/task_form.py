from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Optional

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    start_date = DateTimeLocalField(
        'Fecha de inicio',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    end_date = DateTimeLocalField(
        'Fecha de fin',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    type = SelectField('Tipo', choices=[
        ('study', 'Estudio'),
        ('practice', 'Práctica'),
        ('lab', 'Laboratorio'),
        ('ctf', 'CTF'),
        ('project', 'Proyecto'),
        ('other', 'Otro')
    ])
    color = StringField('Color', default='#007bff')
    completed = BooleanField('Completada')

    # Campos para recurrencia
    recurring = BooleanField('Recurrente')
    days_of_week = SelectMultipleField(
        'Días de la semana',
        choices=[
            ('0', 'Lunes'),
            ('1', 'Martes'),
            ('2', 'Miércoles'),
            ('3', 'Jueves'),
            ('4', 'Viernes'),
            ('5', 'Sábado'),
            ('6', 'Domingo'),
        ]
    )
    start_recur = DateTimeLocalField(
        'Fecha de inicio de recurrencia',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()]
    )
    end_recur = DateTimeLocalField(
        'Fecha de fin de recurrencia',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()]
    )
