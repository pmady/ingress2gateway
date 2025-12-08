FROM python:3.13-slim

WORKDIR /app

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system --no-cache .

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["i2g"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
