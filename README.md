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

## Deploying to Azure Container Apps

### Prerequisites

- Azure CLI (`az`) installed and logged in
- Docker installed
- An existing Azure Container Registry (ACR)
- An existing Container App Environment

### 1. Build and push the Docker image

```powershell
.\build-and-push.ps1 -AcrName <your-acr-name>
```

This builds the image and pushes it as `<your-acr-name>.azurecr.io/hr-mcp-server:latest`.

### 2. Deploy the Container App

```powershell
az deployment group create `
  --resource-group <your-rg> `
  --template-file infra/container-app.bicep `
  --parameters `
    environmentId="/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.App/managedEnvironments/<env-name>" `
    acrLoginServer="<your-acr-name>.azurecr.io" `
    appInsightsConnectionString="<optional-connection-string>"
```

The Bicep template (`infra/container-app.bicep`) creates a Container App with:
- External ingress on port 8000
- System-assigned managed identity for ACR pull
- Application Insights telemetry (optional)

### 3. Grant ACR pull permissions

After deployment, assign the `AcrPull` role to the Container App's managed identity:

```powershell
# Get the principal ID from the deployment output
$principalId = (az containerapp show --name hr-mcp-server --resource-group <your-rg> --query identity.principalId -o tsv)

az role assignment create `
  --assignee $principalId `
  --role AcrPull `
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/<your-acr-name>
```

### 4. Restart the Container App

After the role assignment propagates, restart to pull the image with the managed identity:

```powershell
az containerapp revision restart --name hr-mcp-server --resource-group <your-rg>
```
