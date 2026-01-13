# Employee Evaluation System

A comprehensive Flask-based employee evaluation system with dynamic question management and role-based access control.

## Features

### 🎯 Dynamic Evaluation System

- **Manager-Controlled Questions**: Managers can create, edit, and delete evaluation questions
- **Flexible Answers**: Each question can have multiple predefined answers with optional scores
- **Real-Time Updates**: Changes to questions automatically appear for all supervisors
- **Active/Inactive Toggle**: Control which questions appear in evaluations

### 👥 Role-Based Access Control

#### Manager

- Full CRUD access to supervisors and employees
- Create and manage evaluation questions and answers
- View all evaluations with advanced filtering
- Upload employees via CSV
- Change supervisor passwords
- View aggregated evaluation reports

#### Supervisors

- Evaluate assigned employees using dynamic questions
- View their own employees and evaluations
- Cannot access other supervisors' data

### 📊 Evaluation Features

- **Card-Based UI**: Clean, animated question cards with radio button selections
- **Score Tracking**: Automatic calculation of total and average scores
- **Evaluation History**: Complete audit trail of all evaluations
- **Detailed Reports**: View individual evaluation responses
- **Filtering**: Filter evaluations by employee, supervisor, or date range

### 🎨 UI/UX

- **Soft Animations**: Wave-like transitions and smooth interactions
- **Dark/Light Mode**: Full theme support with persistent preference
- **Responsive Design**: Works on all screen sizes
- **Professional Styling**: Corporate-grade interface with Bootstrap 5

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/mhmdtmrsid-lab/Employee_Evaluation_System.git
cd Employee_Evaluation_System
```

1. **Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Initialize database**

```bash
python seed.py
```

1. **Run the application**

```bash
python run.py
```

1. **Access the application**

- URL: `http://localhost:5000`
- Manager Login: `manager@groupatlantic.com` / `password123`

## Database Schema

### Core Models

#### Supervisor

- Manages authentication and role hierarchy
- Fields: `name`, `email`, `password_hash`, `role`, `manager_id`
- Roles: `manager` or `supervisor`

#### Employee

- Represents workers being evaluated
- Fields: `name`, `employee_code`, `supervisor_id`

#### EvaluationQuestion

- Dynamic questions created by managers
- Fields: `question_text`, `is_active`, `order_index`

#### QuestionAnswer

- Predefined answers for each question
- Fields: `answer_text`, `score`, `order_index`

#### Evaluation

- Main evaluation record
- Links to multiple responses
- Calculates total and average scores

#### EvaluationResponse

- Individual answer to a question
- Links evaluation, question, and selected answer

## Usage Guide

### For Managers

#### 1. Managing Questions

1. Navigate to **Questions** in the navigation bar
2. Click **Add New Question**
3. Enter question text and set display order
4. Toggle active/inactive status
5. Add multiple answer choices with optional scores

#### 2. Managing Answers

1. In the Questions page, expand a question
2. Click **Add Answer**
3. Enter answer text and optional score (0-100)
4. Set display order
5. Edit or delete answers as needed

#### 3. Viewing Evaluations

1. Navigate to **Evaluations** in the navigation bar
2. Use filters to narrow results:
   - Filter by employee
   - Filter by supervisor
   - Filter by date range
3. Click **View Details** to see full evaluation responses

#### 4. Managing Supervisors

1. From Dashboard, click **Add Supervisor**
2. Enter name and email (@groupatlantic.com domain required)
3. Default password: `password123`
4. Use **Change Password** to update supervisor passwords

#### 5. Managing Employees

1. Add employees via supervisor details page
2. Or upload CSV file with format: `Name, Code, SupervisorEmail`

### For Supervisors

#### 1. Evaluating Employees

1. Navigate to **Employees**
2. Click on an employee
3. Answer all evaluation questions (radio buttons)
4. Add optional overall notes
5. Click **Submit Evaluation**

#### 2. Viewing History

- Employee profiles show complete evaluation history
- View dates, scores, and notes for all past evaluations

## API Endpoints

### Question Management (Manager Only)

- `GET /manager/questions` - List all questions
- `POST /manager/questions/add` - Create new question
- `POST /manager/questions/edit/<id>` - Update question
- `POST /manager/questions/delete/<id>` - Delete question (AJAX)

### Answer Management (Manager Only)

- `POST /manager/questions/<question_id>/answers/add` - Add answer
- `POST /manager/answers/edit/<id>` - Update answer
- `POST /manager/answers/delete/<id>` - Delete answer (AJAX)

### Evaluations

- `GET /employee/<id>` - View employee and submit evaluation
- `GET /manager/evaluations` - View all evaluations (Manager)
- `GET /manager/evaluation/<id>` - View evaluation details (Manager)

## Configuration

### Email Domain Validation

By default, all supervisor emails must end with `@groupatlantic.com`.
To change this, edit `app/main/forms.py`:

```python
if not (email.data.endswith('@yourcompany.com') or '@yourcompany.com' in email.data):
    raise ValidationError('Email must belong to @yourcompany.com domain.')
```

### CSRF Protection

CSRF tokens are automatically handled via Flask-WTF. The token is included in the meta tag for AJAX requests.

## Security Features

- **Password Hashing**: Werkzeug security for password storage
- **Role-Based Access**: Strict permission checks on all routes
- **CSRF Protection**: All forms and AJAX requests protected
- **Email Validation**: Domain-restricted supervisor accounts
- **Self-Deletion Prevention**: Managers cannot delete themselves

## Technologies Used

- **Backend**: Flask 2.x
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Security**: Flask-WTF CSRF, Werkzeug password hashing

## File Structure

```
Employee_Evaluation_System/
├── app/
│   ├── __init__.py              # App factory
│   ├── models.py                # Database models
│   ├── auth/                    # Authentication blueprint
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/                    # Main blueprint
│   │   ├── routes.py            # All routes including evaluation system
│   │   └── forms.py             # All forms including dynamic evaluation
│   ├── static/
│   │   ├── css/
│   │   │   ├── theme.css        # Main theme styles
│   │   │   └── animations.css   # Animation definitions
│   │   └── js/
│   │       ├── theme.js         # Dark mode toggle
│   │       ├── search.js        # Table search
│   │       └── delete_buttons.js # AJAX delete handlers
│   └── templates/
│       ├── base.html            # Base template
│       ├── auth/                # Login templates
│       └── main/                # All main templates
│           ├── manager_dashboard.html
│           ├── employee_profile.html
│           ├── manage_questions.html
│           ├── add_question.html
│           ├── edit_question.html
│           ├── add_answer.html
│           ├── edit_answer.html
│           ├── view_evaluations.html
│           └── evaluation_detail.html
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── seed.py                      # Database seeding
└── requirements.txt             # Python dependencies
```

## Sample Data

The seed script creates:

- 1 Manager account
- 5 Sample evaluation questions with 5 answers each:
  1. Work Quality
  2. Teamwork
  3. Communication
  4. Initiative
  5. Reliability

Each answer has a score from 20-100 points.

## Troubleshooting

### Database Issues

If you encounter database errors, reset the database:

```bash
python seed.py
```

### CSRF Token Errors

Ensure the meta tag is present in `base.html`:

```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### Permission Errors

- Verify user role in database
- Check route decorators for `@login_required` and role checks

## Future Enhancements

- [ ] Export evaluations to PDF/Excel
- [ ] Email notifications for new evaluations
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom scoring formulas
- [ ] Evaluation templates
- [ ] Bulk question import

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please contact the development team.
