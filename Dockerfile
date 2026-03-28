FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user required by Hugging Face Spaces
RUN useradd -m -u 1000 user

COPY backend/ /app/
COPY requirements_django.txt /app/

# Install dependencies as root
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements_django.txt

# Grant ownership to the non-root user so the app can write to the directory (e.g. SQLite DB, CFD outputs)
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Collect static files as the user
RUN python manage.py collectstatic --noinput

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "fins_project.wsgi:application"]