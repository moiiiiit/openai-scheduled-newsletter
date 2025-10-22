FROM python:3.10-slim AS test-only
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml ./
COPY . .
RUN rm -rf .venv .pytest_cache
COPY scripts/run_newsletter.sh /app/run_newsletter
RUN chmod +x /app/run_newsletter
RUN poetry config virtualenvs.create false
RUN poetry lock
RUN poetry install --no-interaction --no-ansi --with dev
RUN poetry run pytest --maxfail=1 --disable-warnings

FROM test-only AS prod
WORKDIR /app
CMD ["poetry", "run", "python", "-m", "deepseek_daily_newsletter.main"]
