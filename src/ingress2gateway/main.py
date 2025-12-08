"""FastAPI application for Ingress to Gateway API converter."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .converter import convert_ingress_to_gateway, parse_ingress, resources_to_yaml

app = FastAPI(
    title="Ingress to Gateway API Converter",
    description="Convert Kubernetes Ingress objects to Gateway API resources",
    version="0.1.0",
)


class ConvertRequest(BaseModel):
    """Request model for conversion."""

    ingress_yaml: str


class ConvertResponse(BaseModel):
    """Response model for conversion."""

    gateway_yaml: str
    gateway: dict
    httproutes: list[dict]


@app.post("/api/convert", response_model=ConvertResponse)
async def convert(request: ConvertRequest):
    """Convert Ingress YAML to Gateway API resources."""
    try:
        ingress = parse_ingress(request.ingress_yaml)
        resources = convert_ingress_to_gateway(ingress)
        gateway_yaml = resources_to_yaml(resources)

        return ConvertResponse(
            gateway_yaml=gateway_yaml,
            gateway=resources["gateway"],
            httproutes=resources["httproutes"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main GUI page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ingress to Gateway API Converter</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/yaml/yaml.min.js"></script>
    <style>
        .CodeMirror {
            height: 100%;
            font-size: 14px;
            border-radius: 0.5rem;
        }
        .editor-container {
            height: calc(100vh - 200px);
            min-height: 400px;
        }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-blue-400 mb-2">Ingress to Gateway API Converter</h1>
            <p class="text-gray-400">Convert Kubernetes Ingress objects to Gateway API resources</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Input Panel -->
            <div class="bg-gray-800 rounded-lg p-4 shadow-lg">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-semibold text-blue-300">Ingress YAML</h2>
                    <button onclick="loadExample()" class="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition">
                        Load Example
                    </button>
                </div>
                <div class="editor-container">
                    <textarea id="input-editor"></textarea>
                </div>
            </div>

            <!-- Output Panel -->
            <div class="bg-gray-800 rounded-lg p-4 shadow-lg">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-semibold text-green-300">Gateway API YAML</h2>
                    <button onclick="copyOutput()" class="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition">
                        Copy to Clipboard
                    </button>
                </div>
                <div class="editor-container">
                    <textarea id="output-editor"></textarea>
                </div>
            </div>
        </div>

        <!-- Convert Button -->
        <div class="text-center mt-6">
            <button onclick="convert()" id="convert-btn" class="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-lg transition transform hover:scale-105 shadow-lg">
                Convert →
            </button>
        </div>

        <!-- Error Display -->
        <div id="error-container" class="hidden mt-6 bg-red-900/50 border border-red-500 rounded-lg p-4">
            <p class="text-red-300" id="error-message"></p>
        </div>
    </div>

    <script>
        // Initialize CodeMirror editors
        const inputEditor = CodeMirror.fromTextArea(document.getElementById('input-editor'), {
            mode: 'yaml',
            theme: 'dracula',
            lineNumbers: true,
            lineWrapping: true,
            tabSize: 2,
        });

        const outputEditor = CodeMirror.fromTextArea(document.getElementById('output-editor'), {
            mode: 'yaml',
            theme: 'dracula',
            lineNumbers: true,
            lineWrapping: true,
            tabSize: 2,
            readOnly: true,
        });

        // Example Ingress YAML
        const exampleIngress = `apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - example.com
      secretName: example-tls
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
          - path: /web
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80`;

        function loadExample() {
            inputEditor.setValue(exampleIngress);
        }

        async function convert() {
            const btn = document.getElementById('convert-btn');
            const errorContainer = document.getElementById('error-container');
            const errorMessage = document.getElementById('error-message');

            btn.disabled = true;
            btn.textContent = 'Converting...';
            errorContainer.classList.add('hidden');

            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ingress_yaml: inputEditor.getValue(),
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Conversion failed');
                }

                outputEditor.setValue(data.gateway_yaml);
            } catch (error) {
                errorMessage.textContent = error.message;
                errorContainer.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Convert →';
            }
        }

        function copyOutput() {
            const output = outputEditor.getValue();
            if (output) {
                navigator.clipboard.writeText(output).then(() => {
                    const btn = event.target;
                    const originalText = btn.textContent;
                    btn.textContent = 'Copied!';
                    setTimeout(() => btn.textContent = originalText, 2000);
                });
            }
        }

        // Load example on page load
        loadExample();
    </script>
</body>
</html>
"""


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
