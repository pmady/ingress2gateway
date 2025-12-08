# Provider Presets

ingress2gateway supports multiple Gateway API implementations through provider presets. Each preset configures the appropriate gateway class and provider-specific defaults.

## Available Providers

| Provider | Gateway Class | gRPC Support | TCP Support |
|----------|---------------|--------------|-------------|
| Istio | `istio` | ✓ | ✓ |
| Envoy Gateway | `eg` | ✓ | ✓ |
| Contour | `contour` | ✓ | ✓ |
| Kong | `kong` | ✓ | ✓ |
| NGINX Gateway Fabric | `nginx` | ✗ | ✗ |
| Traefik | `traefik` | ✓ | ✓ |
| GKE Gateway Controller | `gke-l7-global-external-managed` | ✓ | ✗ |

## Provider Details

### Istio

[Istio](https://istio.io/) is a service mesh that includes a Gateway API implementation.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p istio
```

**Configuration:**

- Gateway Class: `istio`
- Namespace scope: Same namespace
- Full gRPC and TCP support

### Envoy Gateway

[Envoy Gateway](https://gateway.envoyproxy.io/) is a Kubernetes Gateway API implementation using Envoy Proxy.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p envoy
```

**Configuration:**

- Gateway Class: `eg`
- Namespace scope: Same namespace
- Full gRPC and TCP support

### Contour

[Contour](https://projectcontour.io/) is an Envoy-based ingress controller with Gateway API support.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p contour
```

**Configuration:**

- Gateway Class: `contour`
- Namespace scope: All namespaces (cross-namespace routing)
- Full gRPC and TCP support

### Kong

[Kong Gateway](https://docs.konghq.com/gateway/) provides Gateway API support through the Kong Ingress Controller.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p kong
```

**Configuration:**

- Gateway Class: `kong`
- Namespace scope: Same namespace
- Adds `konghq.com/strip-path: true` annotation by default
- Full gRPC and TCP support

### NGINX Gateway Fabric

[NGINX Gateway Fabric](https://github.com/nginxinc/nginx-gateway-fabric) is NGINX's Gateway API implementation.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p nginx
```

**Configuration:**

- Gateway Class: `nginx`
- Namespace scope: Same namespace
- No gRPC or TCP support currently

### Traefik

[Traefik](https://traefik.io/) is a cloud-native application proxy with Gateway API support.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p traefik
```

**Configuration:**

- Gateway Class: `traefik`
- Namespace scope: Same namespace
- Full gRPC and TCP support

### GKE Gateway Controller

[GKE Gateway Controller](https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api) is Google Cloud's managed Gateway API implementation.

```bash
ingress2gateway convert ingress.yaml -o gateway.yaml -p gke
```

**Configuration:**

- Gateway Class: `gke-l7-global-external-managed`
- Namespace scope: Same namespace
- gRPC support, no TCP support

## Using Providers in Code

```python
from ingress2gateway import (
    convert_ingress_to_gateway,
    apply_provider_defaults,
    get_provider,
    list_providers,
)

# List all providers
providers = list_providers()
for p in providers:
    print(f"{p['id']}: {p['name']}")

# Get provider configuration
config = get_provider("istio")
print(f"Gateway Class: {config['gateway_class']}")
print(f"Supports gRPC: {config['supports_grpc']}")

# Apply provider defaults to converted resources
resources = convert_ingress_to_gateway(ingress)
resources["gateway"] = apply_provider_defaults(resources["gateway"], "contour")
```

## Custom Gateway Class

If you need to use a custom gateway class not covered by the presets, you can modify the output after conversion:

```python
resources = convert_ingress_to_gateway(ingress)
resources["gateway"]["spec"]["gatewayClassName"] = "my-custom-class"
```

Or edit the YAML output directly:

```bash
ingress2gateway convert ingress.yaml -q | \
  sed 's/gatewayClassName: istio/gatewayClassName: my-custom-class/' > gateway.yaml
```
