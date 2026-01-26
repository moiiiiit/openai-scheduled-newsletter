FROM python:3.10-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy shared library and API service
COPY shared/ ./shared/
COPY openai_scheduled_newsletter_api/ ./openai_scheduled_newsletter_api/

# Configure poetry to not create venv
RUN poetry config virtualenvs.create false

# Install shared library first
WORKDIR /app/shared
RUN poetry install --no-interaction --no-ansi

# Install API service with shared as dependency
WORKDIR /app/openai_scheduled_newsletter_api
RUN poetry install --no-interaction --no-ansi

# Run the API
CMD ["poetry", "run", "python", "-m", "openai_scheduled_newsletter_api.main"]
