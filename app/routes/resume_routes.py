from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models.resume_models import Resume, StatusChangeLogs
from app.models import db
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from sqlalchemy import func

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
    

SLA_SETTINGS = {
    "открыта (загружена в систему)": 24,
    "на проверке": 48,
    "собеседование": 72,
    "принято": 0,
    "отклонено": 0
}

@bp.route('/resume/stats', methods=['GET'])
def get_resume_statistics():
    try:
        stage_durations = calculate_stage_durations()
        
        status_distribution = get_status_distribution()
        
        source_distribution = get_source_distribution()
        
        avg_candidates_per_vacancy = get_avg_candidates_per_vacancy()
        
        sla_violations = get_sla_violations()
        
        return jsonify({
            'stage_durations': stage_durations,
            'status_distribution': status_distribution,
            'source_distribution': source_distribution,
            'avg_candidates_per_vacancy': avg_candidates_per_vacancy,
            'sla_violations': sla_violations
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def calculate_stage_durations():
    logs = StatusChangeLogs.query.order_by(StatusChangeLogs.resume_id, StatusChangeLogs.change_date).all()
    
    stage_durations = defaultdict(list)
    current_resume = None
    prev_log = None
    
    for log in logs:
        if prev_log and prev_log.resume_id == log.resume_id:
            duration = (log.change_date - prev_log.change_date).total_seconds() / 3600  # в часах
            stage_durations[prev_log.new_status].append(duration)
        prev_log = log
    
    avg_durations = {}
    for status, durations in stage_durations.items():
        avg_durations[status] = sum(durations) / len(durations) if durations else 0
    
    return avg_durations

def get_status_distribution():
    status_counts = db.session.query(
        Resume.status,
        func.count(Resume.resume_id)
    ).group_by(Resume.status).all()
    
    return dict(status_counts)

def get_source_distribution():
    source_counts = db.session.query(
        Resume.source,
        func.count(Resume.resume_id)
    ).group_by(Resume.source).all()
    
    return dict(source_counts)

def get_avg_candidates_per_vacancy():
    counts = db.session.query(
        func.count(Resume.resume_id)
    ).group_by(Resume.vacancy).all()
    
    if not counts:
        return 0
    return sum([c[0] for c in counts]) / len(counts)

def get_sla_violations():
    resumes = db.session.query(
        Resume.resume_id,
        Resume.status,
        Resume.date_last_changes
    ).filter(Resume.status.in_(SLA_SETTINGS.keys())).all()
    
    violations = 0
    current_time = datetime.utcnow()
    
    for resume in resumes:
        sla_hours = SLA_SETTINGS.get(resume.status, 0)
        if sla_hours > 0:
            if isinstance(resume.date_last_changes, date):
                date_last_changes = datetime.combine(resume.date_last_changes, datetime.min.time())
            else:
                date_last_changes = resume.date_last_changes

            time_in_stage = (current_time - date_last_changes).total_seconds() / 3600
            if time_in_stage > sla_hours:
                violations += 1
    
    return violations


@bp.route('/resumes', methods=['GET'])
def get_filtered_resumes():
    try:
        stage_filter = request.args.get('stage')
        vacancy_filter = request.args.get('vacancy')
        
        query = Resume.query
        
        if stage_filter:
            query = query.filter(Resume.status == stage_filter)
        if vacancy_filter:
            query = query.filter(Resume.vacancy == vacancy_filter)
        
        resumes = query.all()
        
        result = [{
            'resume_id': r.resume_id,
            'vacancy': r.vacancy,
            'age': r.age,
            'status': r.status,
            'source': r.source,
            'hr_id': r.hr_id,
            'date_last_changes': r.date_last_changes.isoformat() if r.date_last_changes else None
        } for r in resumes]
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@bp.route('/filter_options', methods=['GET'])
def get_filter_options():
    try:
        stages = db.session.query(
            Resume.status.distinct()
        ).filter(Resume.status.isnot(None)).all()
        unique_stages = [s[0] for s in stages if s[0]]
        
        vacancies = db.session.query(
            Resume.vacancy.distinct()
        ).filter(Resume.vacancy.isnot(None)).all()
        unique_vacancies = [v[0] for v in vacancies if v[0]]
        
        return jsonify({
            'unique_stages': unique_stages,
            'unique_vacancies': unique_vacancies
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    
@bp.route('/filter_resumes')
def show_filter_form():
    return render_template('resume_filter.html')