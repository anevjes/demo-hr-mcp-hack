# HR MCP Server

An HR MCP Server built with [FastMCP](https://gofastmcp.com/) that exposes employee directory, profile, salary, and PII data through scope-based authorization.

## Scopes

| Scope | Description |
|---|---|
| `reader` | Access non-PII employee data (name, department, job title, office, etc.) |
| `writer` | Update employee records |
| `restricted` | Access PII / sensitive data (salary, address, tax info, bank details, etc.) |

### Scope mapping to tools

| Tool | Required Scopes |
|---|---|
| `list_employees` | `reader` |
| `get_employee_profile` | `reader` |
| `search_employee_directory` | `reader` |
| `get_org_chart` | `reader` |
| `get_employee_pii` | `restricted` |
| `get_employee_salary` | `restricted` |
| `get_employee_full_record` | `restricted` |
| `get_department_salary_summary` | `restricted` |
| `update_employee_profile` | `writer` |
| `update_employee_salary` | `writer` + `restricted` |
| `update_employee_contact` | `writer` + `restricted` |
| `whoami` | _(any authenticated user)_ |

## Setup

```bash
pip install fastmcp
```

## Running

```bash
# STDIO mode (for MCP clients)
python server.py

# Or via FastMCP CLI
fastmcp run server.py
```

## Mock Data

The server ships with 7 mock employees across departments (Engineering, Data Science, HR, Finance, Operations, Executive). All data is in-memory via `hr_data.py`.
# demo-hr-mcp-hack
