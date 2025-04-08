from flask import Blueprint, request, jsonify, render_template, redirect, url_for
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

@bp.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Валидация
        if not username or not password:
            return render_template('login.html', 
                               error='Все поля обязательны для заполнения')
        
        # Поиск пользователя
        user = User.query.filter_by(username=username).first()
        
        # Проверка пароля
        if user and check_password_hash(user.password, password):
            # Успешная аутентификация
            return redirect(url_for('user.dashboard'))
        else:
            # Неверные данные
            return render_template('login.html', 
                               error='Неверное имя пользователя или пароль')
    
    # GET-запрос - показать форму
    return render_template('login.html')

@bp.route('/dashboard')
def dashboard():
    return "Добро пожаловать в личный кабинет!"

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

