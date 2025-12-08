# Conversion Mapping

This document describes how Kubernetes Ingress fields are mapped to Gateway API resources.

## Overview

A single Ingress resource is converted to:

- **One Gateway** resource
- **One or more HTTPRoute** resources (one per host rule)
- **GRPCRoute** resources (if gRPC backends are detected)

## Field Mapping

### Ingress to Gateway

| Ingress Field | Gateway Field | Notes |
|---------------|---------------|-------|
| `metadata.name` | `metadata.name` | Same name is used |
| `metadata.namespace` | `metadata.namespace` | Same namespace |
| `spec.ingressClassName` | `spec.gatewayClassName` | Mapped to provider gateway class |
| `spec.tls[].hosts` | `spec.listeners[]` | Creates HTTPS listeners |
| `spec.tls[].secretName` | `spec.listeners[].tls.certificateRefs` | TLS certificate reference |
| `spec.rules[].host` | `spec.listeners[]` | Creates HTTP listeners for non-TLS hosts |

### Ingress to HTTPRoute

| Ingress Field | HTTPRoute Field | Notes |
|---------------|-----------------|-------|
| `metadata.name` | `metadata.name` | Suffixed with host name |
| `metadata.namespace` | `metadata.namespace` | Same namespace |
| `spec.rules[].host` | `spec.hostnames[]` | Host matching |
| `spec.rules[].http.paths[].path` | `spec.rules[].matches[].path.value` | Path matching |
| `spec.rules[].http.paths[].pathType` | `spec.rules[].matches[].path.type` | See path type mapping |
| `spec.rules[].http.paths[].backend.service.name` | `spec.rules[].backendRefs[].name` | Service name |
| `spec.rules[].http.paths[].backend.service.port.number` | `spec.rules[].backendRefs[].port` | Service port |

### Path Type Mapping

| Ingress pathType | Gateway API path.type |
|------------------|----------------------|
| `Prefix` | `PathPrefix` |
| `Exact` | `Exact` |
| `ImplementationSpecific` | `PathPrefix` |

## Annotation Mapping

### Nginx Ingress Annotations

| Annotation | Gateway API Equivalent | Notes |
|------------|------------------------|-------|
| `nginx.ingress.kubernetes.io/rewrite-target` | `HTTPRoute.filters[].urlRewrite` | URL rewrite filter |
| `nginx.ingress.kubernetes.io/ssl-redirect` | `HTTPRoute.filters[].requestRedirect` | Redirect to HTTPS |
| `nginx.ingress.kubernetes.io/backend-protocol: GRPC` | Creates `GRPCRoute` | gRPC backend detection |
| `nginx.ingress.kubernetes.io/proxy-body-size` | Warning generated | No direct equivalent |
| `nginx.ingress.kubernetes.io/proxy-connect-timeout` | Warning generated | Provider-specific |
| `nginx.ingress.kubernetes.io/cors-*` | Warning generated | Requires policy attachment |

### Traefik Annotations

| Annotation | Gateway API Equivalent | Notes |
|------------|------------------------|-------|
| `traefik.ingress.kubernetes.io/router.entrypoints` | Warning generated | Listener configuration |
| `traefik.ingress.kubernetes.io/router.priority` | Warning generated | No direct equivalent |
| `traefik.ingress.kubernetes.io/router.middlewares` | Warning generated | Requires policy attachment |

### Istio Annotations

| Annotation | Gateway API Equivalent | Notes |
|------------|------------------------|-------|
| `kubernetes.io/ingress.class: istio` | `gatewayClassName: istio` | Provider selection |

## gRPC Detection

gRPC backends are detected based on:

1. **Annotation**: `nginx.ingress.kubernetes.io/backend-protocol: GRPC`
2. **Port naming**: Service port named `grpc` or `grpc-*`
3. **Port number**: Common gRPC ports (9090, 50051)

When gRPC is detected, a `GRPCRoute` is created instead of `HTTPRoute`:

```yaml
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: GRPCRoute
metadata:
  name: grpc-service-route
spec:
  parentRefs:
    - name: gateway
  hostnames:
    - grpc.example.com
  rules:
    - backendRefs:
        - name: grpc-service
          port: 9090
```

## Examples

### Basic Ingress

**Input:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

**Output:**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: example
  namespace: default
spec:
  gatewayClassName: istio
  listeners:
    - name: http-example-com
      hostname: example.com
      port: 80
      protocol: HTTP
      allowedRoutes:
        namespaces:
          from: Same
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: example-example-com
  namespace: default
spec:
  parentRefs:
    - name: example
      namespace: default
  hostnames:
    - example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-service
          port: 8080
```

### Ingress with TLS

**Input:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-app
  namespace: default
spec:
  tls:
    - hosts:
        - secure.example.com
      secretName: tls-secret
  rules:
    - host: secure.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: secure-service
                port:
                  number: 443
```

**Output:**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: secure-app
  namespace: default
spec:
  gatewayClassName: istio
  listeners:
    - name: https-secure-example-com
      hostname: secure.example.com
      port: 443
      protocol: HTTPS
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: tls-secret
      allowedRoutes:
        namespaces:
          from: Same
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: secure-app-secure-example-com
  namespace: default
spec:
  parentRefs:
    - name: secure-app
      namespace: default
  hostnames:
    - secure.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: secure-service
          port: 443
```

### Ingress with Rewrite Annotation

**Input:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-example
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /api/$1
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /v1/(.*)
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

**Output:**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: rewrite-example-example-com
  namespace: default
spec:
  parentRefs:
    - name: rewrite-example
      namespace: default
  hostnames:
    - example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /v1/
      filters:
        - type: URLRewrite
          urlRewrite:
            path:
              type: ReplacePrefixMatch
              replacePrefixMatch: /api/
      backendRefs:
        - name: api-service
          port: 8080
```

## Reverse Mapping (Gateway API to Ingress)

The tool also supports reverse conversion:

| Gateway API Field | Ingress Field | Notes |
|-------------------|---------------|-------|
| `Gateway.metadata.name` | `Ingress.metadata.name` | Same name |
| `Gateway.spec.gatewayClassName` | `Ingress.spec.ingressClassName` | Mapped to ingress class |
| `Gateway.spec.listeners[].tls` | `Ingress.spec.tls[]` | TLS configuration |
| `HTTPRoute.spec.hostnames[]` | `Ingress.spec.rules[].host` | Host rules |
| `HTTPRoute.spec.rules[].matches[].path` | `Ingress.spec.rules[].http.paths[].path` | Path rules |
| `HTTPRoute.spec.rules[].backendRefs[]` | `Ingress.spec.rules[].http.paths[].backend` | Backend services |

## Supported Features

| Feature | Status |
|---------|--------|
| Basic Ingress conversion | ✓ |
| TLS/HTTPS listeners | ✓ |
| Multi-host Ingress | ✓ |
| Multi-document YAML | ✓ |
| Nginx rewrite annotations | ✓ |
| SSL redirect annotations | ✓ |
| gRPC backend detection | ✓ |
| GRPCRoute generation | ✓ |
| Reverse conversion | ✓ |
| Provider presets | ✓ |
| Validation | ✓ |
| Migration reports | ✓ |

## Limitations

Some features require manual configuration after conversion:

- **Rate limiting**: Requires provider-specific policy attachment
- **CORS**: Requires provider-specific policy attachment
- **Authentication**: Requires provider-specific policy attachment
- **Custom headers**: May require HTTPRoute filters or policy
- **Session affinity**: Provider-specific configuration
- **Canary deployments**: Requires traffic splitting configuration
