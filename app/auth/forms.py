from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        if not email.data.endswith('@groupatlantic.com') and not email.data.endswith('@groupatlantic'): 
             # User said "@groupatlantic" specifically. I should check exactly what the user meant. 
             # "Allow login ONLY if email ends with "@groupatlantic""
             # Usually domains have TLDs. But I will strict check endsWith("@groupatlantic") or maybe it implies the domain part.
             # Request: 'Allow login ONLY if email ends with "@groupatlantic"'
             # It likely implies checking the string suffix. I'll stick to string suffix.
            if not email.data.endswith('@groupatlantic') and not '@groupatlantic.' in email.data:
                 raise ValidationError('Only @groupatlantic emails are allowed.')
