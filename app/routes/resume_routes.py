from flask import Blueprint, request, jsonify, render_template
from app.models.resume_models import Resume, StatusChangeLogs
from app.models import db

bp = Blueprint('resume', __name__)

@bp.route('/resume', methods=['POST'])
def create_resume():
    data = request.form
    resume = Resume(vacancy = data['vacancy'], age = data['age'], status = data['status'], source = data['source'], hr_id = data['hr_id'])
    db.session.add(resume)
    db.session.commit()
    return jsonify({'message': 'Resume created successfully'}), 201

@bp.route('/status', methods=['POST'])
def create_status():
    data = request.form
    status = StatusChangeLogs(resume_id = data['resume_id'], old_status = data['old_status'], new_status = data['new_status'])
    db.session.add(status)
    db.session.commit()
    return jsonify({'message': 'Status created successfully'}), 201
    
@bp.route('/create_resume', methods=['GET'])
def create_resume_form():
    return render_template('create_resume.html')

@bp.route('/create_status', methods=['GET'])
def create_status_form():
    return render_template('create_status.html')