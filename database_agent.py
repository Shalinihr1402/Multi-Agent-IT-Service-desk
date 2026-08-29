import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load DB URL from env or default to SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///service_desk.db")
engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(bind=engine)

def get_employee_device_info(employee_id: int):
    """Return dicts with employee and device info for the given employee_id."""
    with Session() as session:
        emp = session.execute(text("SELECT * FROM employees WHERE id = :eid"), {"eid": employee_id}).first()
        dev = session.execute(text("SELECT * FROM devices WHERE employee_id = :eid"), {"eid": employee_id}).first()
        employee_info = dict(emp) if emp else {}
        device_info = dict(dev) if dev else {}
        return employee_info, device_info
