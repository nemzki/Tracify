from extensions import db

class Visitor(db.Model):
    __tablename__ = 'visitors'

    visitor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    logs = db.relationship('VisitorLog', backref='visitor', lazy=True)
