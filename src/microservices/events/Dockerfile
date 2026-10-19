FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR app/

RUN apt-get update && apt-get install -y netcat-traditional

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod 755 waiter.sh

CMD ./waiter.sh && fastapi run --port 8082
