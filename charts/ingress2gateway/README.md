# ingress2gateway Helm Chart

A Helm chart for deploying the ingress2gateway web UI and API server.

## Installation

```bash
helm repo add ingress2gateway https://pmady.github.io/ingress2gateway
helm install ingress2gateway ingress2gateway/ingress2gateway
```

Or install from local chart:

```bash
helm install ingress2gateway ./charts/ingress2gateway
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `ghcr.io/pmady/ingress2gateway` |
| `image.tag` | Image tag | `""` (uses appVersion) |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable Ingress | `false` |
| `ingress.className` | Ingress class | `""` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `gateway.enabled` | Enable Gateway API | `false` |
| `gateway.className` | Gateway class | `istio` |
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `config.defaultProvider` | Default provider | `istio` |

## Examples

### With Ingress

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: ingress2gateway.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ingress2gateway-tls
      hosts:
        - ingress2gateway.example.com
```

### With Gateway API

```yaml
gateway:
  enabled: true
  className: istio
  listeners:
    - name: http
      port: 80
      protocol: HTTP
  httproute:
    hostnames:
      - ingress2gateway.example.com
```

### With Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```
