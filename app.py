import os
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables (e.g., DB path)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///service_desk.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = sessionmaker(bind=engine)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

# Import agents (local modules)
from manager_agent import classify_ticket
from troubleshooting_agent import troubleshoot
from knowledge_agent import search_knowledge
from database_agent import get_employee_device_info
from response_agent import build_response

@app.route('/')
def index():
    return render_template('ticket.html')

@app.route('/submit', methods=['POST'])
def submit_ticket():
    employee_name = request.form.get('employee_name')
    employee_email = request.form.get('employee_email')
    issue_text = request.form.get('issue')

    # Basic validation
    if not (employee_name and employee_email and issue_text):
        flash('All fields are required.', 'error')
        return redirect(url_for('index'))

    # Persist ticket (basic insert)
    with Session() as session:
        # Ensure employee exists or create
        result = session.execute(text("SELECT id FROM employees WHERE email = :email"), {"email": employee_email}).first()
        if result:
            employee_id = result[0]
        else:
            session.execute(text("INSERT INTO employees (name, email) VALUES (:name, :email)"), {"name": employee_name, "email": employee_email})
            employee_id = session.execute(text("SELECT last_insert_rowid()")).scalar()
        session.commit()
        # Insert ticket
        session.execute(text("INSERT INTO tickets (employee_id, issue) VALUES (:eid, :issue)"), {"eid": employee_id, "issue": issue_text})
        ticket_id = session.execute(text("SELECT last_insert_rowid()")).scalar()
        session.commit()

    # --- Orchestration start ---
    category = classify_ticket(issue_text)
    # Retrieve context
    employee_info, device_info = get_employee_device_info(employee_id)
    # Knowledge search (optional, based on category)
    knowledge_snippets = search_knowledge(issue_text)
    # Generate troubleshooting steps
    steps = troubleshoot(category, issue_text, knowledge_snippets, employee_info, device_info)
    # Build final response and update ticket
    response_text, needs_escalation = build_response(steps, category)
    with Session() as session:
        session.execute(
            text("UPDATE tickets SET response = :resp, status = :status, escalation = :esc WHERE id = :tid"),
            {"resp": response_text, "status": "closed" if not needs_escalation else "escalated", "esc": int(needs_escalation), "tid": ticket_id}
        )
        session.commit()
    # --- Orchestration end ---
    flash('Ticket processed. Check your email for the response.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure DB tables exist (run init script if needed)
    if not os.path.exists('service_desk.db'):
        os.system('python init_db.py')
    app.run(host='0.0.0.0', port=5000, debug=True)
