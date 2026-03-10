FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input
RUN python manage.py migrate --run-syncdb

EXPOSE 7860

CMD ["gunicorn", "womenator_project.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2"]
