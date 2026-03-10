FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SECRET_KEY=build-secret-key
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=*
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@womenovators.com
ENV DJANGO_SUPERUSER_PASSWORD=Womenovators@2026

RUN python manage.py collectstatic --no-input

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 7860

CMD ["/app/start.sh"]
