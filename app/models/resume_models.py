from . import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = 'Resume'
    resume_id = db.Column(db.Integer, primary_key=True)
    vacancy = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_last_changes = db.Column(db.Date, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=False)
    hr_id = db.Column(db.Integer, db.ForeignKey('Hr.hr_id'), nullable=False)
    archiv = db.Column(db.Boolean, default=False)

class StatusChangeLogs(db.Model):
    __tablename__ = 'StatusChangeLogs'
    log_id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('Resume.resume_id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    change_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    


