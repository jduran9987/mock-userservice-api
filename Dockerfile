FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/0.6.3/install.sh | sh

# Explicitly set PATH for all subsequent commands
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# # Install the dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Production stage
FROM python:3.12-slim AS final

# Set the working directory
WORKDIR /app

# Copy venv from builder stage
COPY --from=base /app/.venv /app/.venv

# Update paths
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Copy the rest of the application
COPY src/ .

# Run the application
CMD ["python", "-m", "fastapi", "run", "main.py", "--port", "8000"]
