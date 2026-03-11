from datetime import datetime
from extensions import db
import re


class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(128), nullable=False, index=True)
    translation = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Term {self.term}>"

    def to_dict(self):
        return {
            "id": self.id,
            "term": self.term,
            "translation": self.translation,
            "description": self.description,
        }

    @staticmethod
    def validar_term(term, term_id=None):
        """
        Valida que el termino no esté duplicado en la base de datos y tenga un formato adecuado.

        Args:
            term (str): El termino a validar.
            term_id (int, opcional): ID del termino actual para evitar falsos positivos al editar.

        Returns:
            str: El termino validado.

        Raises:
            ValueError: Si el termino ya existe o es inválido.
        """
        if not term or term.strip() == "":
            raise ValueError("El termino no puede estar vacío")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\-]+$", term):
            raise ValueError(
                "El termino solo puede contener letras, espacios, puntos y guiones"
            )

        # FIX: era `term_id != term_id` (siempre False). Ahora compara el ID del
        # registro encontrado con el ID que se está editando para evitar falsos positivos.
        existing = Term.query.filter_by(term=term).first()
        if existing and (term_id is None or existing.id != term_id):
            raise ValueError("El termino ya existe en la base de datos")

        return term