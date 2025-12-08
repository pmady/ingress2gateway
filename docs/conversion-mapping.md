# Conversion Mapping

This document describes how Kubernetes Ingress fields are mapped to Gateway API resources.

## Overview

A single Ingress resource is converted to:

- **One Gateway** resource
- **One or more HTTPRoute** resources (one per host rule)

## Field Mapping

### Ingress to Gateway

| Ingress Field | Gateway Field | Notes |
|---------------|---------------|-------|
| `metadata.name` | `metadata.name` | Same name is used |
| `metadata.namespace` | `metadata.namespace` | Same namespace |
| `spec.ingressClassName` | `spec.gatewayClassName` | Defaults to "istio" if not specified |
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
  gatewayClassName: nginx
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

## Limitations

The converter currently does not support:

- Ingress annotations (nginx-specific rewrites, rate limits, etc.)
- Multiple TLS certificates per listener
- TCPRoute or UDPRoute generation
- GRPCRoute generation
- Custom filters or request/response modifications

These features may be added in future versions.
