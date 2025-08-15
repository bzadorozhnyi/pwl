# Use the official Python image as the base image
FROM python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.10 /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app/src"

# Create and set the working directory
WORKDIR /app

# Copy the FastAPI application code into the container
COPY . /app/

# Install dependencies
RUN uv sync --locked --no-dev

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Command to run the FastAPI application
CMD ["sh", "./src/entrypoint.sh"]