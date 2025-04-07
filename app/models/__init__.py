from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .resume_models import Resume, StatusChangeLogs
from .user_models import User, Hr, HrLead