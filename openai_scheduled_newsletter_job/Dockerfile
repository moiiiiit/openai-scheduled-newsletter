FROM python:3.10-slim AS test-only
WORKDIR /app

RUN pip install poetry

# Copy shared library and job service
COPY shared/ ./shared/
COPY openai_scheduled_newsletter_job/ ./openai_scheduled_newsletter_job/

RUN rm -rf .venv .pytest_cache
COPY openai_scheduled_newsletter_job/scripts/run_newsletter.sh /app/run_newsletter
RUN chmod +x /app/run_newsletter

# Install shared library first
WORKDIR /app/shared
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Install job service with shared as dependency
WORKDIR /app/openai_scheduled_newsletter_job
RUN poetry config virtualenvs.create false
RUN poetry lock
RUN poetry install --no-interaction --no-ansi
RUN poetry run pytest --maxfail=1 --disable-warnings

FROM test-only AS prod
WORKDIR /app/openai_scheduled_newsletter_job
CMD ["poetry", "run", "python", "-m", "openai_scheduled_newsletter_job.main"]
