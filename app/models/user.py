from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)

    logs = db.relationship('VisitorLog', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='assigned_user', lazy=True)
