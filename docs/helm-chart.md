# Helm Chart

Deploy the ingress2gateway web UI to your Kubernetes cluster using Helm.

## Prerequisites

- Kubernetes 1.21+
- Helm 3.0+

## Installation

### Add Helm Repository

```bash
helm repo add ingress2gateway https://pmady.github.io/ingress2gateway
helm repo update
```

### Install Chart

```bash
# Basic installation
helm install ingress2gateway ingress2gateway/ingress2gateway

# With custom namespace
helm install ingress2gateway ingress2gateway/ingress2gateway -n tools --create-namespace

# With custom values
helm install ingress2gateway ingress2gateway/ingress2gateway -f values.yaml
```

### Install from Source

```bash
git clone https://github.com/pmady/ingress2gateway.git
cd ingress2gateway
helm install ingress2gateway ./charts/ingress2gateway
```

## Configuration

### Basic Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `ghcr.io/pmady/ingress2gateway` |
| `image.tag` | Image tag | `""` (uses appVersion) |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable Ingress | `false` |
| `ingress.className` | Ingress class | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### Gateway API Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `gateway.enabled` | Enable Gateway API | `false` |
| `gateway.className` | Gateway class | `istio` |
| `gateway.listeners` | Gateway listeners | `[{name: http, port: 80, protocol: HTTP}]` |
| `gateway.httproute.hostnames` | HTTPRoute hostnames | `[]` |

### Resources

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.defaultProvider` | Default provider preset | `istio` |
| `config.debug` | Enable debug mode | `false` |
| `config.logLevel` | Log level | `info` |

## Examples

### With Ingress

```yaml
# values-ingress.yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
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

```bash
helm install ingress2gateway ingress2gateway/ingress2gateway -f values-ingress.yaml
```

### With Gateway API

```yaml
# values-gateway.yaml
gateway:
  enabled: true
  className: istio
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
  httproute:
    hostnames:
      - ingress2gateway.example.com
```

```bash
helm install ingress2gateway ingress2gateway/ingress2gateway -f values-gateway.yaml
```

### With Autoscaling

```yaml
# values-autoscaling.yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi
```

### Production Configuration

```yaml
# values-production.yaml
replicaCount: 3

image:
  pullPolicy: Always

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: ingress2gateway.company.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ingress2gateway-tls
      hosts:
        - ingress2gateway.company.com

config:
  defaultProvider: istio
  logLevel: info
```

## Upgrading

```bash
# Update repository
helm repo update

# Upgrade release
helm upgrade ingress2gateway ingress2gateway/ingress2gateway

# Upgrade with new values
helm upgrade ingress2gateway ingress2gateway/ingress2gateway -f values.yaml
```

## Uninstalling

```bash
helm uninstall ingress2gateway
```

## Building the Docker Image

If you need to build the Docker image locally:

```bash
cd ingress2gateway
docker build -t ingress2gateway:local .

# Use local image in Helm
helm install ingress2gateway ./charts/ingress2gateway \
  --set image.repository=ingress2gateway \
  --set image.tag=local \
  --set image.pullPolicy=Never
```

## Troubleshooting

### Pod Not Starting

Check pod logs:

```bash
kubectl logs -l app.kubernetes.io/name=ingress2gateway
```

### Service Not Accessible

Verify service and endpoints:

```bash
kubectl get svc ingress2gateway
kubectl get endpoints ingress2gateway
```

### Health Check Failing

The application exposes `/health` endpoint. Verify it's responding:

```bash
kubectl port-forward svc/ingress2gateway 8000:8000
curl http://localhost:8000/health
```
