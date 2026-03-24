@description('Name of the Container App')
param containerAppName string = 'hr-mcp-server'

@description('Resource ID of the existing Container App Environment')
param environmentId string

@description('ACR login server (e.g. myacr.azurecr.io)')
param acrLoginServer string

@description('Docker image name')
param imageName string = 'hr-mcp-server'

@description('Docker image tag')
param imageTag string = 'latest'

@description('Location for the Container App')
param location string = resourceGroup().location

@description('Application Insights connection string for telemetry')
@secure()
param appInsightsConnectionString string = ''

@description('CPU cores allocated to the container')
param cpuCores string = '0.5'

@description('Memory allocated to the container (e.g. 1Gi)')
param memory string = '1Gi'

@description('Minimum number of replicas')
param minReplicas int = 0

@description('Maximum number of replicas')
param maxReplicas int = 1

@description('Whether to use managed identity for ACR pull (requires acrPull role assignment)')
param useManagedIdentityForAcr bool = true

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  identity: useManagedIdentityForAcr ? {
    type: 'SystemAssigned'
  } : null
  properties: {
    environmentId: environmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
      registries: useManagedIdentityForAcr ? [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: '${acrLoginServer}/${imageName}:${imageTag}'
          resources: {
            cpu: json(cpuCores)
            memory: memory
          }
          env: [
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppId string = containerApp.id
output containerAppIdentityPrincipalId string = useManagedIdentityForAcr ? containerApp.identity.principalId : ''
