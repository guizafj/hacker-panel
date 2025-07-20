from datetime import datetime
from extensions import db

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(128), nullable=False)  # Termino
    translation = db.Column(db.String(128), nullable=False) # Traduccion del termino
    description =description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __repr__(self):
        return f'<Term {self.term}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'translation': self.translation,
            'description': self.description,
        }