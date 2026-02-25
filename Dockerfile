FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir kubernetes redis

COPY agent.py .

CMD ["python", "agent.py"]