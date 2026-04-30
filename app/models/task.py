from datetime import datetime
from extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)

    assigned_to = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    task_description = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='assigned')
