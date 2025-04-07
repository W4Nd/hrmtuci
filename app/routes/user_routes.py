from flask import Blueprint, request, jsonify, render_template
from app.models.user_models import User, Hr, HrLead
from app.models import db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('user', __name__)

@bp.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    try:
        password_hash = generate_password_hash(data['password'])
        user, hr_lead_id = User.create_user_with_role(
            username=data['username'],
            role=data['role'],
            password=password_hash,
            hr_lead_id=data.get('hr_lead_id'),
            sla=data.get('sla')
        )
        
        response_data = {
            "message": "User created successfully",
            "user_id": user.user_id,
            "role": user.role
        }
        
        # Добавляем hr_lead_id только если он есть
        if hr_lead_id is not None:
            response_data['hr_lead_id'] = hr_lead_id
            
        return jsonify(response_data), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@bp.route('/hr', methods=['POST'])
def create_hr():
    data = request.form
    hr = Hr(user_id = data['user_id'], hr_lead_id = data['hr_lead_id'])
    db.session.add(hr)
    db.session.commit()
    return jsonify({'message': 'Hr created successfully'}), 201

@bp.route('/hrlead', methods=['POST'])
def create_hrlead():
    data = request.form
    hrlead = HrLead(user_id = data['user_id'], sla = data['sla'])
    db.session.add(hrlead)
    db.session.commit()
    return jsonify({'message': 'HrLead created successfully'}), 201

@bp.route('/create_user', methods=['GET'])
def create_user_form():
    return render_template('create_user.html')

@bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

