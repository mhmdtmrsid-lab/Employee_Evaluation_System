from app import create_app, db
from app.models import Supervisor, Employee, Evaluation, EvaluationQuestion, QuestionAnswer

app = create_app()

with app.app_context():
    print("=" * 70)
    print("INITIALIZING EMPLOYEE EVALUATION SYSTEM DATABASE")
    print("=" * 70)
    
    # Drop all and recreate to ensure schema is fresh
    print("\n[1/4] Dropping existing database tables...")
    db.drop_all()
    print("      Done.")
    
    print("[2/4] Creating new database schema...")
    db.create_all()
    print("      Done.")

    print("[3/4] Creating Manager account...")
    # Only create the main Manager account
    manager = Supervisor(
        name='Grand Manager', 
        email='manager@groupatlantic.com', 
        role='manager'
    )
    manager.set_password('password123')
    db.session.add(manager)
    db.session.commit()
    print(f"      Manager created: {manager.name} ({manager.email})")
    print(f"      Manager ID: {manager.id}")
    print(f"      Role: {manager.role}")

    print("[4/4] Verifying database initialization...")
    # Verify data was persisted
    supervisor_count = db.session.query(Supervisor).count()
    question_count = db.session.query(EvaluationQuestion).count()
    answer_count = db.session.query(QuestionAnswer).count()
    
    print(f"      Supervisors in DB: {supervisor_count}")
    print(f"      Questions in DB: {question_count}")
    print(f"      Answers in DB: {answer_count}")
    
    # Verify manager can be queried
    verified_manager = db.session.get(Supervisor, manager.id)
    print(f"      Manager verification: {'PASSED' if verified_manager else 'FAILED'}")
    
    print("\n" + "=" * 70)
    print("DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print("\nLogin Credentials:")
    print(f"  Email:    manager@groupatlantic.com")
    print(f"  Password: password123")
    print("\nNext Steps:")
    print("  1. Start the application: python run.py")
    print("  2. Navigate to http://localhost:5000/login")
    print("  3. Log in with the credentials above")
    print("  4. Create evaluation questions via the 'Manage Questions' dashboard")
    print("\nNo evaluation questions have been auto-seeded.")
    print("Manager must create questions manually to enable evaluations.")
    print("=" * 70)

