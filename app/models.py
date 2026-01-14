from datetime import datetime
import calendar
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for Flask-Login session management"""
    try:
        # Use modern SQLAlchemy 2.0 API
        return db.session.get(Supervisor, int(user_id))
    except (ValueError, TypeError):
        return None

class Supervisor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='supervisor')
    
    # Self-referential for Manager -> Supervisors hierarchy
    manager_id = db.Column(db.Integer, db.ForeignKey('supervisor.id'), nullable=True)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='supervisor', lazy=True, cascade='all, delete-orphan')
    employees = db.relationship('Employee', backref='supervisor', lazy=True)
    
    # If this is a manager, they can access supervisors
    subordinates = db.relationship('Supervisor', backref=db.backref('manager', remote_side=[id]), lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_supervisor(self):
        return self.role == 'supervisor'

    def __repr__(self):
        return f"Supervisor('{self.name}', '{self.email}', '{self.role}')"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Link to a specific Supervisor
    supervisor_id = db.Column(db.Integer, db.ForeignKey('supervisor.id'), nullable=False)
    
    # Relationship to evaluations
    evaluations = db.relationship('Evaluation', backref='employee', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Employee('{self.name}', '{self.employee_code}')"

class EvaluationQuestion(db.Model):
    """Dynamic evaluation questions managed by Manager"""
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    order_index = db.Column(db.Integer, default=0)  # For ordering questions
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('QuestionAnswer', backref='question', lazy=True, cascade='all, delete-orphan', order_by='QuestionAnswer.order_index')
    responses = db.relationship('EvaluationResponse', backref='question', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"EvaluationQuestion('{self.question_text[:50]}...')"

class QuestionAnswer(db.Model):
    """Predefined answers for each question"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('evaluation_question.id'), nullable=False)
    answer_text = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=True)  # Optional numeric score
    order_index = db.Column(db.Integer, default=0)  # For ordering answers
    
    # Relationships
    responses = db.relationship('EvaluationResponse', backref='selected_answer', lazy=True)

    def __repr__(self):
        return f"QuestionAnswer('{self.answer_text}', score={self.score})"

class EvaluationCycle(db.Model):
    """Groups evaluations by month and year - for display/organization ONLY, not for blocking"""
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to evaluations
    evaluations = db.relationship('Evaluation', backref='cycle', lazy=True)

    @property
    def name(self):
        return f"{calendar.month_name[self.month]} {self.year}"

    @staticmethod
    def get_or_create_current():
        """Get or create the current month's cycle"""
        now = datetime.utcnow()
        cycle = EvaluationCycle.query.filter_by(month=now.month, year=now.year).first()
        if not cycle:
            cycle = EvaluationCycle(month=now.month, year=now.year)
            db.session.add(cycle)
            db.session.commit()
        return cycle

    def __repr__(self):
        return f"EvaluationCycle({self.month}/{self.year})"

class SystemSettings(db.Model):
    """Global system configuration"""
    id = db.Column(db.Integer, primary_key=True)
    evaluations_enabled = db.Column(db.Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        from sqlalchemy.exc import OperationalError
        try:
            settings = SystemSettings.query.first()
        except OperationalError:
            # Table might not exist, attempt to create
            db.create_all()
            settings = SystemSettings.query.first()

        if not settings:
            # Create default row if missing
            settings = SystemSettings(evaluations_enabled=True)
            db.session.add(settings)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                settings = SystemSettings.query.first()
        return settings

    def __repr__(self):
        return f"SystemSettings(evaluations_enabled={self.evaluations_enabled})"

class Evaluation(db.Model):
    """Main evaluation record - links to multiple responses"""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # Optional overall notes
    
    # Year and Month for this evaluation (immutable once created)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    
    # Foreign Keys
    supervisor_id = db.Column(db.Integer, db.ForeignKey('supervisor.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('evaluation_cycle.id'), nullable=True) # For historical grouping
    
    # Relationships
    responses = db.relationship('EvaluationResponse', backref='evaluation', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_score(self):
        """Calculate total score from all responses"""
        return sum([r.score for r in self.responses if r.score is not None])
    
    @property
    def average_score(self):
        """Calculate average score"""
        scores = [r.score for r in self.responses if r.score is not None]
        return sum(scores) / len(scores) if scores else 0

    def __repr__(self):
        return f"Evaluation(Employee: {self.employee_id}, Supervisor: {self.supervisor_id}, '{self.created_at}')"

class EvaluationResponse(db.Model):
    """Individual response to a question within an evaluation"""
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('evaluation_question.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('question_answer.id'), nullable=False)
    score = db.Column(db.Integer, nullable=True)  # Cached score from answer
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"EvaluationResponse(Q:{self.question_id}, A:{self.answer_id})"
