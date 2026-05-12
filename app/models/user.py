from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'security'

    logs = db.relationship('VisitorLog', backref='user', lazy=True,
                           foreign_keys='VisitorLog.recorded_by')
    tasks = db.relationship('Task', backref='assigned_user', lazy=True,
                            foreign_keys='Task.assigned_to')

    def get_id(self):
        return str(self.user_id)