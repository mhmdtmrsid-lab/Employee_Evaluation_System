from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, HiddenField, PasswordField, BooleanField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo, Optional, NumberRange
from app.models import Employee, Supervisor, EvaluationQuestion
from flask_login import current_user

# ===== EVALUATION QUESTION MANAGEMENT (Manager Only) =====

class QuestionAnswerForm(FlaskForm):
    """Sub-form for individual answers"""
    answer_text = StringField('Answer Text', validators=[DataRequired(), Length(min=1, max=200)])
    score = IntegerField('Score (Optional)', validators=[Optional(), NumberRange(min=0, max=100)])
    order_index = IntegerField('Order', default=0, validators=[Optional()])

class AddQuestionForm(FlaskForm):
    """Form for adding new evaluation questions"""
    question_text = StringField('Question Text', validators=[DataRequired(), Length(min=5, max=500)])
    is_active = BooleanField('Active', default=True)
    order_index = IntegerField('Display Order', default=0, validators=[Optional()])
    submit = SubmitField('Create Question')

class EditQuestionForm(FlaskForm):
    """Form for editing evaluation questions"""
    id = HiddenField('ID')
    question_text = StringField('Question Text', validators=[DataRequired(), Length(min=5, max=500)])
    is_active = BooleanField('Active')
    order_index = IntegerField('Display Order', default=0, validators=[Optional()])
    submit = SubmitField('Update Question')

class AddAnswerForm(FlaskForm):
    """Form for adding answers to a question"""
    question_id = HiddenField('Question ID')
    answer_text = StringField('Answer Text', validators=[DataRequired(), Length(min=1, max=200)])
    score = IntegerField('Score (Optional)', validators=[Optional(), NumberRange(min=0, max=100)])
    order_index = IntegerField('Order', default=0, validators=[Optional()])
    submit = SubmitField('Add Answer')

class EditAnswerForm(FlaskForm):
    """Form for editing an answer"""
    id = HiddenField('ID')
    answer_text = StringField('Answer Text', validators=[DataRequired(), Length(min=1, max=200)])
    score = IntegerField('Score (Optional)', validators=[Optional(), NumberRange(min=0, max=100)])
    order_index = IntegerField('Order', default=0, validators=[Optional()])
    submit = SubmitField('Update Answer')

# ===== DYNAMIC EVALUATION FORM (Supervisor) =====

class DynamicEvaluationForm(FlaskForm):
    """Dynamic form that builds itself based on active questions"""
    notes = TextAreaField('Overall Notes (Optional)', validators=[Length(max=1000)])
    submit = SubmitField('Submit Evaluation')
    
    def __init__(self, *args, **kwargs):
        super(DynamicEvaluationForm, self).__init__(*args, **kwargs)
        # Dynamically add radio fields for each active question
        from app import db
        from app.models import EvaluationQuestion
        
        questions = db.session.query(EvaluationQuestion).filter_by(is_active=True).order_by(EvaluationQuestion.order_index).all()
        
        for question in questions:
            answers = question.answers
            if answers:
                choices = [(str(answer.id), answer.answer_text) for answer in sorted(answers, key=lambda a: a.order_index)]
                field_name = f'question_{question.id}'
                setattr(self, field_name, RadioField(
                    question.question_text,
                    choices=choices,
                    validators=[DataRequired(message="Please select an answer")]
                ))


# ===== LEGACY/SIMPLE EVALUATION (Keep for backward compatibility) =====

class EvaluationForm(FlaskForm):
    rating = SelectField('Rating (1-5)', choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Average'), (4, '4 - Good'), (5, '5 - Excellent')], coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    submit = SubmitField('Submit Evaluation')

# ===== SUPERVISOR MANAGEMENT =====

class AddSupervisorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Create Supervisor')

    def validate_email(self, email):
        user = Supervisor.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use.')
        if not (email.data.endswith('@groupatlantic.com') or '@groupatlantic.com' in email.data):
             raise ValidationError('Email must belong to @groupatlantic.com domain.')

class EditSupervisorForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Supervisor')

    def validate_email(self, email):
        user = Supervisor.query.filter_by(email=email.data).first()
        if user and str(user.id) != self.id.data:
            raise ValidationError('That email is already in use by another account.')
        if not (email.data.endswith('@groupatlantic.com') or '@groupatlantic.com' in email.data):
             raise ValidationError('Email must belong to @groupatlantic.com domain.')

class ChangePasswordForm(FlaskForm):
    id = HiddenField('ID')
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Change Password')

# ===== EMPLOYEE MANAGEMENT =====

class AddEmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    code = StringField('Employee Code', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Add Employee')

    def validate_code(self, code):
        emp = Employee.query.filter_by(employee_code=code.data).first()
        if emp:
            raise ValidationError('Employee code must be unique.')

class EditEmployeeForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    code = StringField('Employee Code', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Update Employee')

    def validate_code(self, code):
        emp = Employee.query.filter_by(employee_code=code.data).first()
        if emp and str(emp.id) != self.id.data:
            raise ValidationError('Employee code must be unique.')

class UploadCSVForm(FlaskForm):
    file = FileField('CSV File', validators=[
        FileRequired(), 
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload CSV')
