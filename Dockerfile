FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir kubernetes redis google-genai

COPY agent.py .

CMD ["python", "-u", "agent.py"]