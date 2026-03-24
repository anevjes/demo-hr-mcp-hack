using 'container-app.bicep'

param containerAppName = 'hr-mcp-server'
param environmentId = '<your-container-app-environment-resource-id>'
param acrLoginServer = '<your-acr-name>.azurecr.io'
param imageName = 'hr-mcp-server'
param imageTag = 'latest'
param appInsightsConnectionString = ''
