"""
HR MCP Server with scope-based authorization using FastMCP.

Scopes:
  - reader     : Access to non-PII employee data (name, department, job title, etc.)
  - writer     : Ability to update non-PII employee records
  - restricted : Access to PII / sensitive data (salary, address, tax info, etc.)
"""

import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from fastmcp import FastMCP
from fastmcp.server.auth import AuthContext, require_scopes, restrict_tag
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.dependencies import get_access_token
from fastmcp.exceptions import AuthorizationError

from hr_data import (
    EMPLOYEES,
    PII_FIELDS,
    PUBLIC_FIELDS,
    get_full_profile,
    get_pii_fields,
    get_public_profile,
    list_all_employee_ids,
    search_employees,
)

# ── Telemetry Setup ──────────────────────────────────────────────────────────

connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(connection_string=connection_string)

logger = logging.getLogger("hr_mcp_server")
logger.setLevel(logging.INFO)

tracer = trace.get_tracer("hr_mcp_server")

# ── Custom Auth Checks ──────────────────────────────────────────────────────


def require_any_scope(*required: str):
    """Factory: returns an auth check that passes if the token has ANY of the given scopes."""
    def check(ctx: AuthContext) -> bool:
        if ctx.token is None:
            raise AuthorizationError("Authentication required")
        return bool(set(required) & set(ctx.token.scopes))
    return check


def check_reader(ctx: AuthContext) -> bool:
    """Custom auth check – requires the 'reader' scope."""
    if ctx.token is None:
        raise AuthorizationError("Authentication required")
    if "reader" not in ctx.token.scopes:
        raise AuthorizationError("The 'reader' scope is required to access this resource")
    return True


def check_writer(ctx: AuthContext) -> bool:
    """Custom auth check – requires the 'writer' scope."""
    if ctx.token is None:
        raise AuthorizationError("Authentication required")
    if "writer" not in ctx.token.scopes:
        raise AuthorizationError("The 'writer' scope is required to perform this action")
    return True


def check_restricted(ctx: AuthContext) -> bool:
    """Custom auth check – requires the 'restricted' scope for PII data access."""
    if ctx.token is None:
        raise AuthorizationError("Authentication required")
    if "restricted" not in ctx.token.scopes:
        raise AuthorizationError(
            "The 'restricted' scope is required to access PII / sensitive data"
        )
    return True


# ── Server Setup ─────────────────────────────────────────────────────────────

mcp = FastMCP(
    "HR MCP Server",
    instructions=(
        "Human Resources MCP Server. Provides employee directory lookups, "
        "profile retrieval, and record updates. Access is governed by three "
        "scopes: 'reader' (public employee data), 'writer' (update records), "
        "and 'restricted' (PII / sensitive data such as salary and address)."
    ),
    middleware=[
        # Tag-based global restrictions: any component tagged 'restricted'
        # automatically requires the 'restricted' scope.
        AuthMiddleware(auth=restrict_tag("restricted", scopes=["restricted"])),
    ],
 
)


# ═══════════════════════════════════════════════════════════════════════════════
#  READER-scope tools & resources (non-PII)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool(auth=check_reader, tags={"reader"})
def list_employees() -> list[str]:
    """List all employee IDs in the directory."""
    with tracer.start_as_current_span("list_employees"):
        logger.info("Listing all employees")
        result = list_all_employee_ids()
        logger.info("Returned %d employee IDs", len(result))
        return result


@mcp.tool(auth=check_reader, tags={"reader"})
def get_employee_profile(employee_id: str) -> dict | str:
    """
    Get the public (non-PII) profile for an employee.

    Returns name, department, job title, office, start date, time in role,
    manager, and employment status.
    """
    with tracer.start_as_current_span("get_employee_profile") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Fetching public profile for employee_id=%s", employee_id)
        profile = get_public_profile(employee_id)
        if profile is None:
            logger.warning("Employee not found: %s", employee_id)
            return f"Employee '{employee_id}' not found."
        logger.info("Returned profile for %s %s", profile["first_name"], profile["last_name"])
        return profile


@mcp.tool(auth=check_reader, tags={"reader"})
def search_employee_directory(
    department: str | None = None,
    job_title_contains: str | None = None,
    status: str | None = None,
) -> list[dict] | str:
    """
    Search the employee directory by department, job title keyword, or status.
    Returns public (non-PII) fields only.
    """
    with tracer.start_as_current_span("search_employee_directory") as span:
        span.set_attribute("filter.department", department or "")
        span.set_attribute("filter.job_title_contains", job_title_contains or "")
        span.set_attribute("filter.status", status or "")
        logger.info("Searching employees: department=%s, title=%s, status=%s", department, job_title_contains, status)
        results = search_employees(department, job_title_contains, status)
        if not results:
            logger.info("No employees matched search criteria")
            return "No employees matched the search criteria."
        logger.info("Search returned %d results", len(results))
        return results


@mcp.tool(auth=check_reader, tags={"reader"})
def get_org_chart(employee_id: str) -> dict | str:
    """
    Get the organisational chart for an employee – their manager and
    direct reports (public fields only).
    """
    with tracer.start_as_current_span("get_org_chart") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Fetching org chart for employee_id=%s", employee_id)
    emp = get_public_profile(employee_id)
    if emp is None:
        logger.warning("Employee not found for org chart: %s", employee_id)
        return f"Employee '{employee_id}' not found."

    manager = None
    if emp.get("manager_id"):
        manager = get_public_profile(emp["manager_id"])

    direct_reports = [
        get_public_profile(eid)
        for eid, e in EMPLOYEES.items()
        if e.get("manager_id") == employee_id
    ]

    return {
        "employee": emp,
        "manager": manager,
        "direct_reports": [r for r in direct_reports if r],
    }


@mcp.resource("employee://{employee_id}/profile", auth=check_reader)
def employee_profile_resource(employee_id: str) -> dict | str:
    """Resource: public profile for an employee."""
    profile = get_public_profile(employee_id)
    if profile is None:
        return f"Employee '{employee_id}' not found."
    return profile


@mcp.prompt(auth=check_reader)
def onboarding_checklist(employee_id: str) -> str:
    """Generate an onboarding checklist prompt for a new employee."""
    profile = get_public_profile(employee_id)
    if profile is None:
        return f"Employee '{employee_id}' not found."
    return (
        f"Create an onboarding checklist for {profile['first_name']} {profile['last_name']}, "
        f"who is joining the {profile['department']} team as a {profile['job_title']} "
        f"based in {profile['office_location']}. Include IT setup, HR orientation, "
        f"team introductions, and first-week goals."
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTRICTED-scope tools & resources (PII / sensitive data)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool(auth=check_restricted, tags={"restricted"})
def get_employee_pii(employee_id: str) -> dict | str:
    """
    Get PII / sensitive data for an employee.

    Includes: date of birth, personal email, phone, home address,
    tax file number, bank details, salary, bonus target, superannuation,
    and emergency contacts.
    """
    with tracer.start_as_current_span("get_employee_pii") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("PII access requested for employee_id=%s", employee_id)
        pii = get_pii_fields(employee_id)
        if pii is None:
            logger.warning("Employee not found for PII request: %s", employee_id)
            return f"Employee '{employee_id}' not found."
        logger.info("PII data returned for employee_id=%s", employee_id)
        return pii


@mcp.tool(auth=check_restricted, tags={"restricted"})
def get_employee_salary(employee_id: str) -> dict | str:
    """Get salary and compensation details for an employee."""
    with tracer.start_as_current_span("get_employee_salary") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Salary access requested for employee_id=%s", employee_id)
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        logger.warning("Employee not found for salary request: %s", employee_id)
        return f"Employee '{employee_id}' not found."
    return {
        "employee_id": employee_id,
        "name": f"{emp['first_name']} {emp['last_name']}",
        "salary": emp["salary"],
        "bonus_target_pct": emp["bonus_target_pct"],
        "superannuation_pct": emp["superannuation_pct"],
        "total_package_estimate": round(
            emp["salary"] * (1 + emp["bonus_target_pct"] / 100 + emp["superannuation_pct"] / 100)
        ),
    }


@mcp.tool(auth=check_restricted, tags={"restricted"})
def get_employee_full_record(employee_id: str) -> dict | str:
    """
    Get the complete employee record including all PII fields.
    Requires the 'restricted' scope.
    """
    with tracer.start_as_current_span("get_employee_full_record") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Full record access requested for employee_id=%s", employee_id)
        record = get_full_profile(employee_id)
        if record is None:
            logger.warning("Employee not found for full record: %s", employee_id)
            return f"Employee '{employee_id}' not found."
        logger.info("Full record returned for employee_id=%s", employee_id)
        return record


@mcp.tool(auth=check_restricted, tags={"restricted"})
def get_department_salary_summary(department: str) -> dict | str:
    """
    Get aggregated salary statistics for a department.
    Requires the 'restricted' scope.
    """
    with tracer.start_as_current_span("get_department_salary_summary") as span:
        span.set_attribute("department", department)
        logger.info("Department salary summary requested for department=%s", department)
    dept_employees = [
        e for e in EMPLOYEES.values()
        if e["department"].lower() == department.lower()
    ]
    if not dept_employees:
        logger.warning("No employees found in department: %s", department)
        return f"No employees found in department '{department}'.'"

    salaries = [e["salary"] for e in dept_employees]
    return {
        "department": department,
        "headcount": len(dept_employees),
        "min_salary": min(salaries),
        "max_salary": max(salaries),
        "avg_salary": round(sum(salaries) / len(salaries)),
        "total_salary_cost": sum(salaries),
    }


@mcp.resource("employee://{employee_id}/pii", auth=check_restricted, tags={"restricted"})
def employee_pii_resource(employee_id: str) -> dict | str:
    """Resource: PII / sensitive data for an employee. Requires 'restricted' scope."""
    pii = get_pii_fields(employee_id)
    if pii is None:
        return f"Employee '{employee_id}' not found."
    return pii


@mcp.resource("employee://{employee_id}/salary", auth=check_restricted, tags={"restricted"})
def employee_salary_resource(employee_id: str) -> dict | str:
    """Resource: Salary & compensation details. Requires 'restricted' scope."""
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        return f"Employee '{employee_id}' not found."
    return {
        "salary": emp["salary"],
        "bonus_target_pct": emp["bonus_target_pct"],
        "superannuation_pct": emp["superannuation_pct"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  WRITER-scope tools (mutate employee records)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool(auth=check_writer, tags={"writer"})
def update_employee_profile(
    employee_id: str,
    department: str | None = None,
    job_title: str | None = None,
    office_location: str | None = None,
    employment_status: str | None = None,
) -> dict | str:
    """
    Update non-PII fields on an employee profile.
    Only the provided fields will be changed.
    """
    with tracer.start_as_current_span("update_employee_profile") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Profile update requested for employee_id=%s", employee_id)
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        logger.warning("Employee not found for profile update: %s", employee_id)
        return f"Employee '{employee_id}' not found."

    updated_fields: dict[str, str] = {}
    if department is not None:
        emp["department"] = department
        updated_fields["department"] = department
    if job_title is not None:
        emp["job_title"] = job_title
        updated_fields["job_title"] = job_title
    if office_location is not None:
        emp["office_location"] = office_location
        updated_fields["office_location"] = office_location
    if employment_status is not None:
        emp["employment_status"] = employment_status
        updated_fields["employment_status"] = employment_status

    if not updated_fields:
        return "No fields were provided to update."

    logger.info("Profile updated for employee_id=%s, fields=%s", employee_id, list(updated_fields.keys()))
    return {"employee_id": employee_id, "updated": updated_fields}


@mcp.tool(auth=[check_writer, check_restricted], tags={"writer", "restricted"})
def update_employee_salary(
    employee_id: str,
    salary: int | None = None,
    bonus_target_pct: int | None = None,
) -> dict | str:
    """
    Update salary / compensation for an employee.
    Requires BOTH 'writer' AND 'restricted' scopes since salary is PII.
    """
    with tracer.start_as_current_span("update_employee_salary") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Salary update requested for employee_id=%s", employee_id)
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        logger.warning("Employee not found for salary update: %s", employee_id)
        return f"Employee '{employee_id}' not found."

    updated_fields: dict[str, int] = {}
    if salary is not None:
        emp["salary"] = salary
        updated_fields["salary"] = salary
    if bonus_target_pct is not None:
        emp["bonus_target_pct"] = bonus_target_pct
        updated_fields["bonus_target_pct"] = bonus_target_pct

    if not updated_fields:
        return "No fields were provided to update."

    return {"employee_id": employee_id, "updated": updated_fields}


@mcp.tool(auth=[check_writer, check_restricted], tags={"writer", "restricted"})
def update_employee_contact(
    employee_id: str,
    phone_number: str | None = None,
    home_address: str | None = None,
    personal_email: str | None = None,
    emergency_contact_name: str | None = None,
    emergency_contact_phone: str | None = None,
) -> dict | str:
    """
    Update PII contact details for an employee.
    Requires BOTH 'writer' AND 'restricted' scopes.
    """
    with tracer.start_as_current_span("update_employee_contact") as span:
        span.set_attribute("employee_id", employee_id)
        logger.info("Contact update requested for employee_id=%s", employee_id)
    emp = EMPLOYEES.get(employee_id)
    if emp is None:
        logger.warning("Employee not found for contact update: %s", employee_id)
        return f"Employee '{employee_id}' not found."

    updated_fields: dict[str, str] = {}
    for field_name, value in [
        ("phone_number", phone_number),
        ("home_address", home_address),
        ("personal_email", personal_email),
        ("emergency_contact_name", emergency_contact_name),
        ("emergency_contact_phone", emergency_contact_phone),
    ]:
        if value is not None:
            emp[field_name] = value
            updated_fields[field_name] = value

    if not updated_fields:
        return "No fields were provided to update."

    return {"employee_id": employee_id, "updated": updated_fields}


# ═══════════════════════════════════════════════════════════════════════════════
#  Utility – whoami (any authenticated user)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def whoami() -> dict:
    """Return information about the current authenticated user and their scopes."""
    token = get_access_token()
    if token is None:
        return {"authenticated": False, "message": "No token present (STDIO mode or unauthenticated)"}
    return {
        "authenticated": True,
        "client_id": token.client_id,
        "scopes": token.scopes,
        "claims": token.claims,
    }


# ── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting HR MCP Server on 0.0.0.0:8000 (streamable-http)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, stateless_http=False)