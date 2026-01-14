import csv
import io
from flask import render_template, request, redirect, url_for, flash, abort, send_file, jsonify
from flask_login import login_required, current_user
from app.main import main
from app.models import Employee, Evaluation, Supervisor, EvaluationQuestion, QuestionAnswer, EvaluationResponse, EvaluationCycle, SystemSettings
from app.main.forms import (EvaluationForm, AddSupervisorForm, AddEmployeeForm, EditSupervisorForm, 
                             EditEmployeeForm, UploadCSVForm, ChangePasswordForm, DynamicEvaluationForm,
                             AddQuestionForm, EditQuestionForm, AddAnswerForm, EditAnswerForm)
from app import db
from werkzeug.utils import secure_filename
from datetime import datetime

# --- DASHBOARD & SHARED ---

@main.route("/")
@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_manager:
        supervisors = Supervisor.query.filter_by(role='supervisor').all()
        all_employees = Employee.query.all()
        total_employees = len(all_employees)
        
        all_evals = Evaluation.query.all()
        total_questions = EvaluationQuestion.query.filter_by(is_active=True).count()
        
        # Calculate average score from new system
        avg_score = 0
        if all_evals:
            scores = [e.average_score for e in all_evals if e.responses]
            avg_score = sum(scores) / len(scores) if scores else 0
        
        pwd_form = ChangePasswordForm()
        cycles = EvaluationCycle.query.order_by(EvaluationCycle.year.desc(), EvaluationCycle.month.desc()).all()
        settings = SystemSettings.get_settings()
        
        return render_template('main/manager_dashboard.html', 
                               supervisors=supervisors,
                               employees=all_employees,
                               total_employees=total_employees,
                               avg_rating=avg_score,
                               total_questions=total_questions,
                               pwd_form=pwd_form,
                               cycles=cycles,
                               settings=settings)
    else:
        # Supervisor Dashboard
        my_employees = Employee.query.filter_by(supervisor_id=current_user.id).all()
        total_my_employees = len(my_employees)
        my_evaluations_count = Evaluation.query.filter_by(supervisor_id=current_user.id).count()
        recent_evals = Evaluation.query.filter_by(supervisor_id=current_user.id).order_by(Evaluation.created_at.desc()).limit(5).all()
        
        return render_template('main/dashboard.html', 
                               total_employees=total_my_employees,
                               my_evaluations=my_evaluations_count,
                               recent_evals=recent_evals)

@main.route("/employees")
@login_required
def employees():
    if current_user.is_manager:
        employees_list = Employee.query.all()
    else:
        employees_list = Employee.query.filter_by(supervisor_id=current_user.id).all()
    return render_template('main/employees.html', employees=employees_list)

@main.route("/employee/<int:employee_id>", methods=['GET', 'POST'])
@login_required
def employee_profile(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Access Control: Only Manager or Direct Supervisor
    if not (current_user.is_manager or employee.supervisor_id == current_user.id):
        abort(403)
    
    # Get active questions for template
    questions = EvaluationQuestion.query.filter_by(is_active=True).order_by(EvaluationQuestion.order_index).all()
    current_cycle = EvaluationCycle.get_or_create_current()
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        # ONLY check SystemSettings.evaluations_enabled - this is the single source of truth
        if not settings.evaluations_enabled:
            flash('Evaluations are currently disabled by the Manager.', 'danger')
            return redirect(url_for('main.employee_profile', employee_id=employee_id))
        
        # Prevent submission if no questions exist
        if not questions:
            flash('No evaluation questions have been created yet. Please ask the manager to create questions.', 'danger')
            return redirect(url_for('main.employee_profile', employee_id=employee_id))

        # Create main evaluation record with year and month
        now = datetime.utcnow()
        evaluation = Evaluation(
            supervisor_id=current_user.id,
            employee_id=employee.id,
            notes=request.form.get('notes', ''),
            cycle_id=current_cycle.id,
            year=now.year,
            month=now.month
        )
        db.session.add(evaluation)
        db.session.flush()
        
        # Process each question response
        for question in questions:
            field_name = f'question_{question.id}'
            answer_id = request.form.get(field_name)
            if answer_id:
                answer = QuestionAnswer.query.get(int(answer_id))
                if answer:
                    response = EvaluationResponse(
                        evaluation_id=evaluation.id,
                        question_id=question.id,
                        answer_id=answer.id,
                        score=answer.score
                    )
                    db.session.add(response)
        
        db.session.commit()
        flash('Evaluation submitted successfully!', 'success')
        return redirect(url_for('main.employee_profile', employee_id=employee_id))
    
    return render_template('main/employee_profile.html', employee=employee, questions=questions, current_cycle=current_cycle, settings=settings)


# --- EVALUATION QUESTIONS MANAGEMENT (Manager Only) ---

@main.route("/manager/questions")
@login_required
def manage_questions():
    if not current_user.is_manager: abort(403)
    questions = EvaluationQuestion.query.order_by(EvaluationQuestion.order_index).all()
    return render_template('main/manage_questions.html', questions=questions)

@main.route("/manager/questions/add", methods=['GET', 'POST'])
@login_required
def add_question():
    if not current_user.is_manager: abort(403)
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = EvaluationQuestion(
            question_text=form.question_text.data,
            is_active=form.is_active.data,
            order_index=form.order_index.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('main.manage_questions'))
    return render_template('main/add_question.html', form=form, title='Add Question')

@main.route("/manager/questions/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_question(id):
    if not current_user.is_manager: abort(403)
    question = EvaluationQuestion.query.get_or_404(id)
    form = EditQuestionForm(obj=question)
    form.id.data = str(id)
    
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.is_active = form.is_active.data
        question.order_index = form.order_index.data
        question.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('main.manage_questions'))
    
    return render_template('main/edit_question.html', form=form, question=question, title='Edit Question')

@main.route("/manager/questions/delete/<int:id>", methods=['POST'])
@login_required
def delete_question(id):
    if not current_user.is_manager: return jsonify(success=False, message="Unauthorized"), 403
    
    try:
        question = EvaluationQuestion.query.get_or_404(id)
        db.session.delete(question)
        db.session.commit()
        return jsonify(success=True, message=f"Question deleted successfully.")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

@main.route("/manager/questions/<int:question_id>/answers/add", methods=['GET', 'POST'])
@login_required
def add_answer(question_id):
    if not current_user.is_manager: abort(403)
    question = EvaluationQuestion.query.get_or_404(question_id)
    form = AddAnswerForm()
    form.question_id.data = question_id
    
    if form.validate_on_submit():
        answer = QuestionAnswer(
            question_id=question_id,
            answer_text=form.answer_text.data,
            score=form.score.data,
            order_index=form.order_index.data
        )
        db.session.add(answer)
        db.session.commit()
        flash('Answer added successfully!', 'success')
        return redirect(url_for('main.manage_questions'))
    
    return render_template('main/add_answer.html', form=form, question=question, title='Add Answer')

@main.route("/manager/answers/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_answer(id):
    if not current_user.is_manager: abort(403)
    answer = QuestionAnswer.query.get_or_404(id)
    form = EditAnswerForm(obj=answer)
    form.id.data = str(id)
    
    if form.validate_on_submit():
        answer.answer_text = form.answer_text.data
        answer.score = form.score.data
        answer.order_index = form.order_index.data
        db.session.commit()
        flash('Answer updated successfully!', 'success')
        return redirect(url_for('main.manage_questions'))
    
    return render_template('main/edit_answer.html', form=form, answer=answer, title='Edit Answer')

@main.route("/manager/answers/delete/<int:id>", methods=['POST'])
@login_required
def delete_answer(id):
    if not current_user.is_manager: return jsonify(success=False, message="Unauthorized"), 403
    
    try:
        answer = QuestionAnswer.query.get_or_404(id)
        db.session.delete(answer)
        db.session.commit()
        return jsonify(success=True, message="Answer deleted successfully.")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

# --- EVALUATION REPORTS (Manager) ---

@main.route("/manager/evaluations")
@login_required
def view_evaluations():
    if not current_user.is_manager: abort(403)
    
    # Get filter parameters
    employee_id = request.args.get('employee_id', type=int)
    supervisor_id = request.args.get('supervisor_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    # Build query - use year and month directly from Evaluation
    query = Evaluation.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if supervisor_id:
        query = query.filter_by(supervisor_id=supervisor_id)
    if year:
        query = query.filter_by(year=year)
    if month:
        query = query.filter_by(month=month)
    
    evaluations = query.order_by(Evaluation.created_at.desc()).all()
    employees = Employee.query.all()
    supervisors = Supervisor.query.filter_by(role='supervisor').all()
    
    return render_template('main/view_evaluations.html', 
                           evaluations=evaluations,
                           employees=employees,
                           supervisors=supervisors)

@main.route("/manager/evaluation/<int:id>")
@login_required
def evaluation_detail(id):
    if not current_user.is_manager: abort(403)
    evaluation = Evaluation.query.get_or_404(id)
    return render_template('main/evaluation_detail.html', evaluation=evaluation)

@main.route("/manager/export-csv/<int:cycle_id>")
@login_required
def export_csv_cycle(cycle_id):
    if not current_user.is_manager: abort(403)
    
    cycle = EvaluationCycle.query.get_or_404(cycle_id)
    
    # Get all evaluations for this cycle (read-only, no modifications)
    evaluations = Evaluation.query.filter_by(cycle_id=cycle.id).all()
    
    # Get all questions (ordered)
    questions = EvaluationQuestion.query.order_by(EvaluationQuestion.order_index).all()
    
    # Create CSV in memory - no database changes
    si = io.StringIO()
    si.write('\ufeff')
    cw = csv.writer(si)
    
    # Header
    header = ['Worker Name', 'Worker Code', 'Supervisor Email']
    for q in questions:
        header.append(q.question_text)
    cw.writerow(header)
    
    # Rows
    for e in evaluations:
        row = [e.employee.name, e.employee.employee_code, e.supervisor.email]
        # Map question responses for this evaluation
        responses = {r.question_id: r.selected_answer.answer_text for r in e.responses}
        for q in questions:
            row.append(responses.get(q.id, ''))
        cw.writerow(row)
    
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    filename = f"evaluations_{cycle.year}_{cycle.month:02d}.csv"
    
    # Return file without any database modifications
    return send_file(output, mimetype='text/csv; charset=utf-8', as_attachment=True, download_name=filename)

@main.route("/manager/settings/toggle-evaluations", methods=['POST'])
@login_required
def toggle_evaluations():
    if not current_user.is_manager: abort(403)
    settings = SystemSettings.get_settings()
    settings.evaluations_enabled = not settings.evaluations_enabled
    db.session.commit()
    status = "enabled" if settings.evaluations_enabled else "disabled"
    flash(f"Evaluations successfully {status}.", "success")
    return redirect(url_for('main.dashboard'))

# --- MANAGER CRUD ROUTES ---

@main.route("/manager/add_supervisor", methods=['GET', 'POST'])
@login_required
def add_supervisor():
    if not current_user.is_manager: abort(403)
    form = AddSupervisorForm()
    if form.validate_on_submit():
        supervisor = Supervisor(name=form.name.data, 
                                email=form.email.data,
                                role='supervisor',
                                manager_id=current_user.id)
        supervisor.set_password('password123')
        db.session.add(supervisor)
        db.session.commit()
        flash(f'Supervisor {form.name.data} created.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/add_supervisor.html', form=form, title='Add Supervisor')

@main.route("/manager/edit_supervisor/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_supervisor(id):
    if not current_user.is_manager: abort(403)
    supervisor = Supervisor.query.get_or_404(id)
    form = EditSupervisorForm(obj=supervisor)
    form.id.data = str(id)
    
    if form.validate_on_submit():
        supervisor.name = form.name.data
        supervisor.email = form.email.data
        db.session.commit()
        flash(f'Supervisor {supervisor.name} updated.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/edit_supervisor.html', form=form, title='Edit Supervisor')

@main.route("/manager/change_password", methods=['POST'])
@login_required
def change_password():
    if not current_user.is_manager: abort(403)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user_id = form.id.data
        supervisor = Supervisor.query.get_or_404(user_id)
        if supervisor.is_manager and supervisor.id != current_user.id:
             pass 
        supervisor.set_password(form.password.data)
        db.session.commit()
        flash(f'Password updated for {supervisor.name}', 'success')
    else:
        for err in form.password.errors: flash(err, 'danger')
        for err in form.confirm_password.errors: flash(err, 'danger')
    return redirect(url_for('main.dashboard'))

@main.route("/manager/delete_supervisor/<int:id>", methods=['POST'])
@login_required
def delete_supervisor(id):
    if not current_user.is_manager: return jsonify(success=False, message="Unauthorized"), 403
    if id == current_user.id:
        return jsonify(success=False, message="You cannot delete yourself."), 400
        
    supervisor = Supervisor.query.get_or_404(id)
    try:
        if supervisor.employees:
             for emp in supervisor.employees:
                 db.session.delete(emp)
        db.session.delete(supervisor)
        db.session.commit()
        return jsonify(success=True, message=f"Supervisor {supervisor.name} deleted.")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

@main.route("/manager/supervisor/<int:supervisor_id>", methods=['GET', 'POST'])
@login_required
def supervisor_details(supervisor_id):
    if not current_user.is_manager: abort(403)
    supervisor = Supervisor.query.get_or_404(supervisor_id)
    form = AddEmployeeForm()
    if form.validate_on_submit():
        emp = Employee(name=form.name.data,
                       employee_code=form.code.data,
                       supervisor_id=supervisor.id)
        db.session.add(emp)
        db.session.commit()
        flash(f'Employee {emp.name} added.', 'success')
        return redirect(url_for('main.supervisor_details', supervisor_id=supervisor.id))
    return render_template('main/supervisor_details.html', supervisor=supervisor, form=form)

@main.route("/manager/edit_employee/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    if not current_user.is_manager: abort(403)
    emp = Employee.query.get_or_404(id)
    form = EditEmployeeForm(obj=emp)
    if request.method == 'GET': form.code.data = emp.employee_code
    form.id.data = str(id)
    if form.validate_on_submit():
        emp.name = form.name.data
        emp.employee_code = form.code.data
        db.session.commit()
        flash(f'Employee {emp.name} updated.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/edit_employee.html', form=form, title='Edit Employee')

@main.route("/manager/delete_employee/<int:id>", methods=['POST'])
@login_required
def delete_employee(id):
    if not current_user.is_manager: return jsonify(success=False, message="Unauthorized"), 403
    
    try:
        emp = Employee.query.get_or_404(id)
        db.session.delete(emp)
        db.session.commit()
        return jsonify(success=True, message=f"Employee {emp.name} deleted.")
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

@main.route("/manager/upload_csv", methods=['GET', 'POST'])
@login_required
def upload_csv():
    if not current_user.is_manager: abort(403)
    form = UploadCSVForm()
    if form.validate_on_submit():
        f = form.file.data
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        rows_processed = 0
        errors = []
        for i, row in enumerate(csv_input):
            if i == 0 and "Name" in row[0]: continue 
            if len(row) < 3:
                errors.append(f"Row {i+1}: Not enough columns.")
                continue
            name = row[0].strip()
            code = row[1].strip()
            sup_email = row[2].strip()
            supervisor = Supervisor.query.filter_by(email=sup_email).first()
            if not supervisor:
                errors.append(f"Row {i+1}: Supervisor {sup_email} not found.")
                continue
            if Employee.query.filter_by(employee_code=code).first():
                errors.append(f"Row {i+1}: Code {code} already exists.")
                continue
            new_emp = Employee(name=name, employee_code=code, supervisor_id=supervisor.id)
            db.session.add(new_emp)
            rows_processed += 1
        if rows_processed > 0:
            try:
                db.session.commit()
                flash(f'Successfully added {rows_processed} employees.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Database error: {str(e)}', 'danger')
        if errors:
            for err in errors[:5]: flash(err, 'warning')
            if len(errors) > 5: flash(f'... and {len(errors)-5} more errors.', 'warning')
        return redirect(url_for('main.dashboard'))
    return render_template('main/upload_csv.html', form=form)
