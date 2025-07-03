A Helm chart for Kubernetes

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Set affinity |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"Always"` | Set the Image Pull Policy |
| image.repository | string | `"nginx"` | Repository of the container image |
| image.tag | string | `""` | Override the chart version. Defaults to `appVersion` of the helm chart. |
| imagePullSecrets | list | `[]` | This is for the secrets for pulling an image from a private repository |
| livenessProbe.httpGet.path | string | `"/"` | Path to use for the livenessProbe |
| livenessProbe.httpGet.port | string | `"http"` | Port to use for the livenessProbe |
| nameOverride | string | `""` | Override the Chart Name |
| nodeSelector | object | `{}` | Configure nodeSelector |
| podAnnotations | object | `{}` | Additional Annotations to apply to Service and Deployment/Pod Objects |
| podLabels | object | `{}` | Additional Labels to apply to Service and Deployment/Pod Objects |
| podSecurityContext | object | `{}` | Set pod-level security context |
| readinessProbe.httpGet.path | string | `"/"` | Path to use for the readinessProbe |
| readinessProbe.httpGet.port | string | `"http"` | Port to use for the readinessProbe |
| replicaCount | int | `1` | Replica Count for version-checker |
| resources | object | `{}` | Setup version-checkers resource requests/limits |
| secrets.auth.name | string | `""` |  |
| secrets.auth.path | string | `""` |  |
| secrets.auth.type | string | `"vault"` |  |
| secrets.config.nameConfig | string | `""` |  |
| secrets.existingSecret | string | `""` |  |
| securityContext | object | `{}` | Set container-level security context |
| service.annotations | object | `{}` | Additional annotations to add to the service |
| service.port | int | `80` | Port to expose within the service |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| serviceMonitor.additionalLabels | object | `{}` | Additional labels to add to the ServiceMonitor |
| serviceMonitor.enabled | bool | `true` | Disable/Enable ServiceMonitor Object |
| tolerations | list | `[]` | Configure tolerations |
| versionChecker.allowedNamespaces | list | `[]` |  |
| versionChecker.configPath | string | `""` |  |
| volumeMounts | list | `[]` | Allow for extra Volume Mounts to version-checkers container |
| volumes | list | `[]` | Allow for extra Volumes to be associated to the pod |
