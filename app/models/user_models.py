from . import db


class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    @classmethod
    def create_user_with_role(cls, username, role, password, **kwargs):
        user = cls(username=username, role=role, password=password)
        db.session.add(user)
        db.session.flush()  # Получаем user_id
    
        hr_lead_id = None
    
        if role == 'hr':
            hr_lead_id = kwargs.get('hr_lead_id')
            if not hr_lead_id:
                raise ValueError("hr_lead_id is required for hr role")
            hr = Hr(user_id=user.user_id, hr_lead_id=hr_lead_id)
            db.session.add(hr)
        
        elif role == 'hr_lead':
            sla = kwargs.get('sla', 'default_sla')
            hr_lead = HrLead(user_id=user.user_id, sla=sla)
            db.session.add(hr_lead)
            db.session.flush()  # Получаем hr_lead_id
            hr_lead_id = hr_lead.hr_lead_id  # ID только что созданного HR Lead
    
        db.session.commit()
        return user, hr_lead_id  # Возвращаем и пользователя, и hr_lead_id
    
class Hr(db.Model):
    __tablename__ = 'Hr'
    hr_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    hr_lead_id = db.Column(db.Integer, db.ForeignKey('HrLead.hr_lead_id'), nullable=False)

class HrLead(db.Model):
    __tablename__ = 'HrLead'
    hr_lead_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    sla = db.Column(db.String(100), nullable=False)

