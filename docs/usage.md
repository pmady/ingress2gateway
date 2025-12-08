# Usage

## Web Interface

The web interface provides an interactive way to convert Ingress resources.

### Steps

1. **Start the server**

   ```bash
   uv run uvicorn src.ingress2gateway.main:app --reload
   ```

2. **Open the browser** at <http://localhost:8000>

3. **Paste your Ingress YAML** in the left editor panel

4. **Click "Convert"** to generate Gateway API resources

5. **Copy the output** using the "Copy to Clipboard" button

### Features

- **Load Example**: Click to load a sample Ingress configuration
- **Syntax Highlighting**: YAML editors with Dracula theme
- **Error Display**: Clear error messages for invalid input

## REST API

### Convert Endpoint

**POST** `/api/convert`

Convert Ingress YAML to Gateway API resources.

#### Request

```json
{
  "ingress_yaml": "apiVersion: networking.k8s.io/v1\nkind: Ingress\n..."
}
```

#### Response

```json
{
  "gateway_yaml": "apiVersion: gateway.networking.k8s.io/v1\nkind: Gateway\n...",
  "gateway": { ... },
  "httproutes": [ ... ]
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "ingress_yaml": "apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: example\nspec:\n  rules:\n    - host: example.com\n      http:\n        paths:\n          - path: /\n            pathType: Prefix\n            backend:\n              service:\n                name: my-service\n                port:\n                  number: 80"
  }'
```

### Health Check

**GET** `/health`

Returns the health status of the application.

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

### OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
