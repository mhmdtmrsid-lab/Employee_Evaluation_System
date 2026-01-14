# Employee Evaluation System

Employee Evaluation System: A Flask web app to manage supervisors, employees, and evaluation cycles with CSV export, dynamic questions, and dark/light mode support.

## Features

- **Supervisor Management** - Create and manage supervisors with role-based access
- **Employee Management** - Add and track employees across the organization
- **Dynamic Evaluation Questions** - Create and customize evaluation questions
- **Evaluation Cycles** - Manage evaluation periods and track completion status
- **CSV Export** - Export evaluation data for reporting and analysis
- **Dark/Light Mode** - User-friendly theme toggle for comfortable viewing
- **Authentication** - Secure login system with session management
- **Responsive Design** - Works seamlessly on desktop and mobile devices

## Technology Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite (configurable for production databases)
- **Frontend:** HTML5, CSS3, JavaScript
- **Email Validation:** email-validator

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mhmdtmrsid-lab/Employee_Evaluation_System.git
cd Employee_Evaluation_System
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python seed.py
```

5. Run the application:
```bash
python run.py
```

6. Open your browser and navigate to:
```
http://localhost:5000/login
```

## Default Credentials

After running `seed.py`, log in with:
- **Email:** manager@groupatlantic.com
- **Password:** password123

## Usage

### Manager Dashboard
- Create evaluation questions
- Manage supervisors and employees
- View and export evaluation results

### Supervisor Features
- Complete employee evaluations
- View evaluation questions and guidelines
- Track evaluation progress

### Employee Features
- View evaluation feedback
- Track evaluation status

## Configuration

Edit `config.py` to customize:
- Database URI
- Secret key
- Session settings

For production deployments, ensure:
- `SECRET_KEY` is set via environment variable
- `DATABASE_URL` points to a production database
- `.env` file is created with sensitive credentials (not tracked in git)

## Deployment

The application includes a `Procfile` for easy deployment to platforms like Heroku:

```bash
git push heroku main
```

## Project Structure

```
.
├── app/
│   ├── auth/              # Authentication routes
│   ├── main/              # Main application routes
│   ├── static/            # CSS and JavaScript files
│   ├── templates/         # HTML templates
│   └── models.py          # Database models
├── instance/              # Instance-specific files (git-ignored)
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
├── seed.py                # Database initialization script
└── Procfile               # Deployment configuration
```

## Environment Variables

Create a `.env` file (not tracked in git) with:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///site.db
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is provided as-is for educational and professional use.

## Support

For issues or questions, please open an issue on the GitHub repository.
