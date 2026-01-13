from app import create_app, db
from app.models import Supervisor, Employee, Evaluation, EvaluationQuestion, QuestionAnswer

app = create_app()

with app.app_context():
    # Drop all and recreate to ensure schema is fresh
    db.drop_all()
    db.create_all()

    print("Creating Manager...")
    # Only create the main Manager account
    manager = Supervisor(name='Grand Manager', email='manager@groupatlantic.com', role='manager')
    manager.set_password('password123')
    db.session.add(manager)
    db.session.commit()

    print("Creating Sample Evaluation Questions...")
    
    # Question 1: Work Quality
    q1 = EvaluationQuestion(
        question_text="How would you rate the employee's work quality?",
        is_active=True,
        order_index=1
    )
    db.session.add(q1)
    db.session.flush()
    
    answers_q1 = [
        QuestionAnswer(question_id=q1.id, answer_text="Excellent - Consistently exceeds expectations", score=100, order_index=1),
        QuestionAnswer(question_id=q1.id, answer_text="Good - Meets and sometimes exceeds expectations", score=80, order_index=2),
        QuestionAnswer(question_id=q1.id, answer_text="Satisfactory - Meets basic expectations", score=60, order_index=3),
        QuestionAnswer(question_id=q1.id, answer_text="Needs Improvement - Below expectations", score=40, order_index=4),
        QuestionAnswer(question_id=q1.id, answer_text="Unsatisfactory - Significantly below expectations", score=20, order_index=5),
    ]
    db.session.add_all(answers_q1)
    
    # Question 2: Teamwork
    q2 = EvaluationQuestion(
        question_text="How well does the employee collaborate with team members?",
        is_active=True,
        order_index=2
    )
    db.session.add(q2)
    db.session.flush()
    
    answers_q2 = [
        QuestionAnswer(question_id=q2.id, answer_text="Outstanding team player", score=100, order_index=1),
        QuestionAnswer(question_id=q2.id, answer_text="Good collaborator", score=80, order_index=2),
        QuestionAnswer(question_id=q2.id, answer_text="Adequate teamwork", score=60, order_index=3),
        QuestionAnswer(question_id=q2.id, answer_text="Limited collaboration", score=40, order_index=4),
        QuestionAnswer(question_id=q2.id, answer_text="Poor team player", score=20, order_index=5),
    ]
    db.session.add_all(answers_q2)
    
    # Question 3: Communication
    q3 = EvaluationQuestion(
        question_text="How effective is the employee's communication?",
        is_active=True,
        order_index=3
    )
    db.session.add(q3)
    db.session.flush()
    
    answers_q3 = [
        QuestionAnswer(question_id=q3.id, answer_text="Excellent communicator", score=100, order_index=1),
        QuestionAnswer(question_id=q3.id, answer_text="Good communication skills", score=80, order_index=2),
        QuestionAnswer(question_id=q3.id, answer_text="Adequate communication", score=60, order_index=3),
        QuestionAnswer(question_id=q3.id, answer_text="Needs improvement", score=40, order_index=4),
        QuestionAnswer(question_id=q3.id, answer_text="Poor communication", score=20, order_index=5),
    ]
    db.session.add_all(answers_q3)
    
    # Question 4: Initiative
    q4 = EvaluationQuestion(
        question_text="Does the employee show initiative and proactivity?",
        is_active=True,
        order_index=4
    )
    db.session.add(q4)
    db.session.flush()
    
    answers_q4 = [
        QuestionAnswer(question_id=q4.id, answer_text="Highly proactive and self-motivated", score=100, order_index=1),
        QuestionAnswer(question_id=q4.id, answer_text="Shows good initiative", score=80, order_index=2),
        QuestionAnswer(question_id=q4.id, answer_text="Adequate initiative", score=60, order_index=3),
        QuestionAnswer(question_id=q4.id, answer_text="Limited initiative", score=40, order_index=4),
        QuestionAnswer(question_id=q4.id, answer_text="Lacks initiative", score=20, order_index=5),
    ]
    db.session.add_all(answers_q4)
    
    # Question 5: Reliability
    q5 = EvaluationQuestion(
        question_text="How reliable and dependable is the employee?",
        is_active=True,
        order_index=5
    )
    db.session.add(q5)
    db.session.flush()
    
    answers_q5 = [
        QuestionAnswer(question_id=q5.id, answer_text="Extremely reliable", score=100, order_index=1),
        QuestionAnswer(question_id=q5.id, answer_text="Very dependable", score=80, order_index=2),
        QuestionAnswer(question_id=q5.id, answer_text="Generally reliable", score=60, order_index=3),
        QuestionAnswer(question_id=q5.id, answer_text="Somewhat unreliable", score=40, order_index=4),
        QuestionAnswer(question_id=q5.id, answer_text="Unreliable", score=20, order_index=5),
    ]
    db.session.add_all(answers_q5)
    
    db.session.commit()

    print("Database reset! Manager account and sample questions created.")
    print("Manager Login: manager@groupatlantic.com / password123")
    print(f"Created {EvaluationQuestion.query.count()} evaluation questions")
