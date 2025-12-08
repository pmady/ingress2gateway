ingress2gateway Documentation
=============================

Convert Kubernetes Ingress objects to Gateway API resources.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   usage
   api
   conversion-mapping

Features
--------

- **Web GUI**: Interactive interface with YAML editors
- **REST API**: Programmatic conversion via ``/api/convert`` endpoint
- **Real-time conversion**: Instant feedback with syntax highlighting
- **Copy to clipboard**: Easy export of converted resources

Quick Start
-----------

.. code-block:: bash

   # Install with uv
   uv sync
   uv run uvicorn src.ingress2gateway.main:app --reload

   # Or with pip
   pip install -e .
   uvicorn src.ingress2gateway.main:app --reload

Then open http://localhost:8000 in your browser.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
