from datetime import datetime
from extensions import db

class VisitorLog(db.Model):
    __tablename__ = 'visitor_logs'

    visitor_log_id = db.Column(db.Integer, primary_key=True)

    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.visitor_id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    purpose_of_visit = db.Column(db.Text, nullable=False)

    time_in = db.Column(db.DateTime, default=datetime.utcnow)
    time_out = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default='active')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)