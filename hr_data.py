"""Mock HR data for the HR MCP Server."""

from datetime import date

# ── Mock Employee Database ──────────────────────────────────────────────────
EMPLOYEES: dict[str, dict] = {
    "EMP001": {
        # Public / reader-level fields
        "employee_id": "EMP001",
        "first_name": "Alice",
        "last_name": "Johnson",
        "department": "Engineering",
        "job_title": "Senior Software Engineer",
        "office_location": "Sydney, AU",
        "start_date": "2019-03-15",
        "time_in_role_years": 4.2,
        "manager_id": "EMP005",
        "employment_status": "Active",
        # PII / restricted fields
        "date_of_birth": "1990-06-22",
        "personal_email": "alice.johnson@personal.com",
        "phone_number": "+61 412 345 678",
        "home_address": "42 Harbour St, Sydney NSW 2000",
        "tax_file_number": "123-456-789",
        "bank_account_bsb": "062-000",
        "bank_account_number": "1234 5678",
        "salary": 185000,
        "bonus_target_pct": 15,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Bob Johnson",
        "emergency_contact_phone": "+61 412 999 888",
    },
    "EMP002": {
        "employee_id": "EMP002",
        "first_name": "Marcus",
        "last_name": "Chen",
        "department": "Data Science",
        "job_title": "Lead Data Scientist",
        "office_location": "Melbourne, AU",
        "start_date": "2020-07-01",
        "time_in_role_years": 3.0,
        "manager_id": "EMP005",
        "employment_status": "Active",
        "date_of_birth": "1985-11-03",
        "personal_email": "marcus.chen@personal.com",
        "phone_number": "+61 422 111 222",
        "home_address": "7 Collins St, Melbourne VIC 3000",
        "tax_file_number": "987-654-321",
        "bank_account_bsb": "033-000",
        "bank_account_number": "8765 4321",
        "salary": 195000,
        "bonus_target_pct": 15,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Li Chen",
        "emergency_contact_phone": "+61 433 222 111",
    },
    "EMP003": {
        "employee_id": "EMP003",
        "first_name": "Sarah",
        "last_name": "Nguyen",
        "department": "Human Resources",
        "job_title": "HR Business Partner",
        "office_location": "Perth, AU",
        "start_date": "2021-01-11",
        "time_in_role_years": 2.5,
        "manager_id": "EMP006",
        "employment_status": "Active",
        "date_of_birth": "1992-02-14",
        "personal_email": "sarah.nguyen@personal.com",
        "phone_number": "+61 455 333 444",
        "home_address": "15 St Georges Tce, Perth WA 6000",
        "tax_file_number": "456-789-012",
        "bank_account_bsb": "016-000",
        "bank_account_number": "1122 3344",
        "salary": 140000,
        "bonus_target_pct": 10,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Tran Nguyen",
        "emergency_contact_phone": "+61 455 777 888",
    },
    "EMP004": {
        "employee_id": "EMP004",
        "first_name": "James",
        "last_name": "Williams",
        "department": "Finance",
        "job_title": "Financial Analyst",
        "office_location": "Brisbane, AU",
        "start_date": "2022-09-05",
        "time_in_role_years": 1.3,
        "manager_id": "EMP006",
        "employment_status": "Active",
        "date_of_birth": "1995-08-30",
        "personal_email": "james.williams@personal.com",
        "phone_number": "+61 477 555 666",
        "home_address": "88 Queen St, Brisbane QLD 4000",
        "tax_file_number": "789-012-345",
        "bank_account_bsb": "084-000",
        "bank_account_number": "5566 7788",
        "salary": 115000,
        "bonus_target_pct": 10,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Karen Williams",
        "emergency_contact_phone": "+61 488 666 555",
    },
    "EMP005": {
        "employee_id": "EMP005",
        "first_name": "Priya",
        "last_name": "Patel",
        "department": "Engineering",
        "job_title": "VP of Engineering",
        "office_location": "Sydney, AU",
        "start_date": "2017-05-20",
        "time_in_role_years": 3.8,
        "manager_id": "EMP007",
        "employment_status": "Active",
        "date_of_birth": "1982-04-17",
        "personal_email": "priya.patel@personal.com",
        "phone_number": "+61 499 777 888",
        "home_address": "200 George St, Sydney NSW 2000",
        "tax_file_number": "321-654-987",
        "bank_account_bsb": "062-000",
        "bank_account_number": "9988 7766",
        "salary": 280000,
        "bonus_target_pct": 25,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Raj Patel",
        "emergency_contact_phone": "+61 499 888 999",
    },
    "EMP006": {
        "employee_id": "EMP006",
        "first_name": "David",
        "last_name": "Kim",
        "department": "Operations",
        "job_title": "Chief Operating Officer",
        "office_location": "Sydney, AU",
        "start_date": "2016-02-01",
        "time_in_role_years": 5.0,
        "manager_id": "EMP007",
        "employment_status": "Active",
        "date_of_birth": "1978-12-09",
        "personal_email": "david.kim@personal.com",
        "phone_number": "+61 400 111 222",
        "home_address": "10 Macquarie St, Sydney NSW 2000",
        "tax_file_number": "654-321-098",
        "bank_account_bsb": "062-000",
        "bank_account_number": "4455 6677",
        "salary": 320000,
        "bonus_target_pct": 30,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Soo-Jin Kim",
        "emergency_contact_phone": "+61 400 333 444",
    },
    "EMP007": {
        "employee_id": "EMP007",
        "first_name": "Emma",
        "last_name": "Thompson",
        "department": "Executive",
        "job_title": "Chief Executive Officer",
        "office_location": "Sydney, AU",
        "start_date": "2015-01-10",
        "time_in_role_years": 8.5,
        "manager_id": None,
        "employment_status": "Active",
        "date_of_birth": "1975-07-25",
        "personal_email": "emma.thompson@personal.com",
        "phone_number": "+61 400 999 000",
        "home_address": "1 Circular Quay, Sydney NSW 2000",
        "tax_file_number": "111-222-333",
        "bank_account_bsb": "062-000",
        "bank_account_number": "1010 2020",
        "salary": 450000,
        "bonus_target_pct": 40,
        "superannuation_pct": 11.5,
        "emergency_contact_name": "Michael Thompson",
        "emergency_contact_phone": "+61 400 000 111",
    },
}

# Fields that are considered PII / restricted
PII_FIELDS = {
    "date_of_birth",
    "personal_email",
    "phone_number",
    "home_address",
    "tax_file_number",
    "bank_account_bsb",
    "bank_account_number",
    "salary",
    "bonus_target_pct",
    "superannuation_pct",
    "emergency_contact_name",
    "emergency_contact_phone",
}

# Fields visible to readers (non-PII)
PUBLIC_FIELDS = {
    "employee_id",
    "first_name",
    "last_name",
    "department",
    "job_title",
    "office_location",
    "start_date",
    "time_in_role_years",
    "manager_id",
    "employment_status",
}


def get_public_profile(employee_id: str) -> dict | None:
    """Return only the non-PII fields for an employee."""
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        return None
    return {k: v for k, v in emp.items() if k in PUBLIC_FIELDS}


def get_full_profile(employee_id: str) -> dict | None:
    """Return the complete employee record including PII."""
    return EMPLOYEES.get(employee_id)


def get_pii_fields(employee_id: str) -> dict | None:
    """Return only the PII / restricted fields for an employee."""
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        return None
    return {k: v for k, v in emp.items() if k in PII_FIELDS}


def list_all_employee_ids() -> list[str]:
    """Return all employee IDs."""
    return list(EMPLOYEES.keys())


def search_employees(
    department: str | None = None,
    job_title_contains: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """Search employees by department, job title keyword, or status. Returns public fields only."""
    results = []
    for emp in EMPLOYEES.values():
        if department and emp["department"].lower() != department.lower():
            continue
        if job_title_contains and job_title_contains.lower() not in emp["job_title"].lower():
            continue
        if status and emp["employment_status"].lower() != status.lower():
            continue
        results.append({k: v for k, v in emp.items() if k in PUBLIC_FIELDS})
    return results
