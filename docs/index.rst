ingress2gateway Documentation
=============================

A comprehensive tool to convert Kubernetes Ingress objects to Gateway API resources with CLI, Web UI, and GitHub Action support.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   usage
   cli
   api
   providers
   conversion-mapping
   github-action
   kubectl-plugin
   helm-chart

Features
--------

Core Conversion
~~~~~~~~~~~~~~~

- **Ingress → Gateway API**: Convert Ingress to Gateway + HTTPRoute resources
- **Gateway API → Ingress**: Reverse conversion for migration rollback
- **Multi-document YAML**: Process multiple Ingress resources at once
- **GRPCRoute Support**: Automatic detection and conversion of gRPC backends
- **TCPRoute/UDPRoute**: Support for TCP and UDP backend services
- **ReferenceGrant**: Auto-generate ReferenceGrants for cross-namespace references

Annotation Support
~~~~~~~~~~~~~~~~~~

- **Nginx Ingress**: Rewrite rules, SSL redirect, CORS, rate limiting
- **Traefik**: Middlewares, entrypoints, priorities
- **Istio**: Ingress class, revision labels
- **AWS ALB**: Certificate ARN, target type, scheme, actions
- **GCE/GKE**: Static IP, managed certificates, backend config

Provider Presets
~~~~~~~~~~~~~~~~

- Istio, Envoy Gateway, Contour, Kong, NGINX Gateway Fabric, Traefik, GKE

User Interfaces
~~~~~~~~~~~~~~~

- **Web GUI**: Interactive interface with dark/light theme, diff view, validation
- **CLI Tool**: Full-featured command-line interface
- **REST API**: Programmatic conversion endpoints
- **GitHub Action**: CI/CD integration for automated conversion
- **kubectl Plugin**: Native kubectl integration
- **Helm Chart**: Deploy web UI to Kubernetes

Additional Features
~~~~~~~~~~~~~~~~~~~

- **Validation**: Input and output schema validation
- **Migration Reports**: Detailed markdown reports with manual steps
- **Download Options**: Single YAML, separate files, or Kustomize structure

Quick Start
-----------

.. code-block:: bash

   # Install
   pip install ingress2gateway

   # CLI usage
   ingress2gateway convert ingress.yaml -o gateway.yaml

   # Start web server
   ingress2gateway serve --port 8000

Then open http://localhost:8000 in your browser.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
