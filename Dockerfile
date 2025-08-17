# Use the official Python image as the base image
FROM python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /uvx /bin/

# Create and set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy dependency files
COPY pyproject.toml uv.lock /app/

# Copy the FastAPI application code into the container
COPY src /app/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Command to run the FastAPI application
CMD ["sh", "./entrypoint.sh"]
