<#
.SYNOPSIS
    Build and push the HR MCP Server Docker image to Azure Container Registry.

.PARAMETER AcrName
    The name of the Azure Container Registry (without .azurecr.io).

.PARAMETER ImageName
    The Docker image name. Defaults to 'hr-mcp-server'.

.PARAMETER Tag
    The image tag. Defaults to 'latest'.

.EXAMPLE
    .\build-and-push.ps1 -AcrName myacr
    .\build-and-push.ps1 -AcrName myacr -Tag v1.0.0
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$AcrName,

    [string]$ImageName = "hr-mcp-server",

    [string]$Tag = "latest"
)

$ErrorActionPreference = "Stop"

$acrLoginServer = "$AcrName.azurecr.io"
$fullImageName = "$acrLoginServer/${ImageName}:${Tag}"

Write-Host "Logging in to ACR: $acrLoginServer" -ForegroundColor Cyan
az acr login --name $AcrName
if ($LASTEXITCODE -ne 0) { throw "ACR login failed." }

Write-Host "Building Docker image: $fullImageName" -ForegroundColor Cyan
docker build -t $fullImageName .
if ($LASTEXITCODE -ne 0) { throw "Docker build failed." }

Write-Host "Pushing image to ACR: $fullImageName" -ForegroundColor Cyan
docker push $fullImageName
if ($LASTEXITCODE -ne 0) { throw "Docker push failed." }

Write-Host "Done. Image pushed: $fullImageName" -ForegroundColor Green
