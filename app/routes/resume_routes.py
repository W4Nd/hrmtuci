from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models.resume_models import Resume, StatusChangeLogs
from app.models import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('resume', __name__)

@bp.route('/')
def index():
    return redirect(url_for('resume.show_create_resume_form'))


@bp.route('/resume', methods=['POST'])
def create_resume():
    data = request.form
    try:
        initial_status = "открыта (загружена в систему)"
        
        resume = Resume(
            vacancy=data['vacancy'],
            age=data['age'],
            status=initial_status,
            date_last_changes=datetime.utcnow(),
            source=data['source'],
            hr_id=data['hr_id'],
            archiv=False
        )
        db.session.add(resume)
        db.session.flush()
        
        status_log = StatusChangeLogs(
            resume_id=resume.resume_id,
            old_status="",
            new_status=initial_status,
            change_date=datetime.utcnow()
        )
        db.session.add(status_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Resume created successfully',
            'resume_id': resume.resume_id
        }), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@bp.route('/resume/<int:resume_id>/status', methods=['PUT'])
def change_resume_status(resume_id):
    data = request.json
    if 'new_status' not in data:
        return jsonify({'error': 'Missing new_status parameter'}), 400
    
    success, message = update_resume_status(resume_id, data['new_status'])
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 500


@bp.route('/resume/<int:resume_id>/status', methods=['GET'])
def get_resume_status(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    return jsonify({
        'current_status': resume.status,
        'last_updated': resume.date_last_changes.isoformat()
    })


@bp.route('/resume/<int:resume_id>/status/history', methods=['GET'])
def get_status_history(resume_id):
    logs = StatusChangeLogs.query.filter_by(resume_id=resume_id)\
                                .order_by(StatusChangeLogs.change_date.desc())\
                                .all()
    return jsonify([{
        'old_status': log.old_status,
        'new_status': log.new_status,
        'change_date': log.change_date.isoformat()
    } for log in logs])


@bp.route('/create_resume')
def show_create_resume_form():
    return render_template('create_resume.html')


@bp.route('/change_status')
def show_change_status_form():
    resume_id = request.args.get('resume_id')
    if not resume_id:
        flash('Resume ID not provided', 'error')
        return redirect(url_for('show_create_resume_form'))
    
    resume = Resume.query.get(resume_id)
    if not resume:
        flash('Resume not found', 'error')
        return redirect(url_for('show_create_resume_form'))
    
    return render_template('change_status.html', 
                         resume_id=resume_id,
                         current_status=resume.status)


def update_resume_status(resume_id, new_status):
    try:
        resume = Resume.query.get(resume_id)
        if not resume:
            return False, "Resume not found"
        
        old_status = resume.status
        resume.status = new_status
        resume.date_last_changes = datetime.utcnow()
        
        status_log = StatusChangeLogs(
            resume_id=resume_id,
            old_status=old_status,
            new_status=new_status,
            change_date=datetime.utcnow()
        )
        db.session.add(status_log)
        db.session.commit()
        return True, "Status updated successfully"
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Server error: {str(e)}"