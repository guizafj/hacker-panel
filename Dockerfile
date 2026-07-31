FROM python:3.13.5-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p instance data/write_ups data/scripts data/theory
CMD ["sh", "-c", "flask db upgrade && flask scan-directories && gunicorn --bind 0.0.0.0:8000 app:app"]

# docker run -p 8000:8000 seguro-app
