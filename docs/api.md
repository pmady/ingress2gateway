# API Reference

## Converter Module

The core conversion logic is in `src/ingress2gateway/converter.py`.

### Functions

#### `parse_ingress(ingress_yaml: str) -> dict`

Parse an Ingress YAML string into a Python dictionary.

**Parameters:**
- `ingress_yaml`: A string containing valid Ingress YAML

**Returns:**
- A dictionary representing the Ingress object

**Raises:**
- `ValueError`: If the YAML is invalid

**Example:**

```python
from src.ingress2gateway.converter import parse_ingress

ingress = parse_ingress("""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
""")
```

#### `convert_ingress_to_gateway(ingress: dict) -> dict`

Convert an Ingress dictionary to Gateway API resources.

**Parameters:**
- `ingress`: A dictionary representing a Kubernetes Ingress object

**Returns:**
- A dictionary with keys:
  - `gateway`: The Gateway resource
  - `httproutes`: A list of HTTPRoute resources

**Raises:**
- `ValueError`: If the ingress is empty or has wrong kind

**Example:**

```python
from src.ingress2gateway.converter import convert_ingress_to_gateway

resources = convert_ingress_to_gateway(ingress)
print(resources["gateway"])
print(resources["httproutes"])
```

#### `resources_to_yaml(resources: dict) -> str`

Convert Gateway API resources to a YAML string.

**Parameters:**
- `resources`: A dictionary with `gateway` and `httproutes` keys

**Returns:**
- A multi-document YAML string

**Example:**

```python
from src.ingress2gateway.converter import resources_to_yaml

yaml_output = resources_to_yaml(resources)
print(yaml_output)
```

## REST API

### POST /api/convert

Convert Ingress YAML to Gateway API resources.

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| `ingress_yaml` | string | The Ingress YAML to convert |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `gateway_yaml` | string | Combined YAML output |
| `gateway` | object | The Gateway resource |
| `httproutes` | array | List of HTTPRoute resources |

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Invalid input (bad YAML or wrong kind) |
| 500 | Internal server error |

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```
