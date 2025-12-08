# Contributing to ingress2gateway

Thank you for your interest in contributing to ingress2gateway! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows the [CNCF Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md). By participating, you are expected to uphold this code.

## Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/) to ensure that contributors have the right to submit their contributions.

### What is DCO?

The DCO is a lightweight way for contributors to certify that they wrote or otherwise have the right to submit the code they are contributing. The DCO agreement is shown below and at <https://developercertificate.org/>:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

### How to Sign Off

You must sign off on each commit by adding a `Signed-off-by` line to your commit message:

```
This is my commit message

Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically by using the `-s` or `--signoff` flag when committing:

```bash
git commit -s -m "Your commit message"
```

If you've already made commits without signing off, you can amend the last commit:

```bash
git commit --amend -s
```

Or rebase to sign off multiple commits:

```bash
git rebase --signoff HEAD~<number-of-commits>
```

## How to Contribute

### Reporting Issues

- Check existing issues to avoid duplicates
- Use the issue templates when available
- Provide clear reproduction steps for bugs
- Include relevant environment information

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`

2. **Set up the development environment**:

   ```bash
   git clone https://github.com/YOUR_USERNAME/ingress2gateway.git
   cd ingress2gateway
   uv sync --all-extras
   ```

3. **Make your changes**:
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests and linting**:

   ```bash
   uv run pytest
   uv run ruff check .
   uv run ruff format --check .
   ```

5. **Sign off your commits** (see DCO section above)

6. **Push and create a Pull Request**:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass

### Code Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Write docstrings for public functions and classes
- Keep functions focused and reasonably sized

### Testing

- Write tests for new features and bug fixes
- Maintain or improve code coverage
- Use pytest for testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ingress2gateway
```

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Quick Start

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ingress2gateway.git
cd ingress2gateway

# Install dependencies
uv sync --all-extras

# Run the application
uv run uvicorn src.ingress2gateway.main:app --reload

# Run tests
uv run pytest
```

## License

By contributing to ingress2gateway, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

## Questions?

If you have questions, feel free to:

- Open a [GitHub Discussion](https://github.com/pmady/ingress2gateway/discussions)
- Create an issue for bugs or feature requests

Thank you for contributing! 🎉
