FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/server

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
