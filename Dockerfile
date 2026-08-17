FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY fixtures ./fixtures
COPY docs ./docs
COPY README.md ARCHITECTURE.md COMPLIANCE.md DEMO_SCRIPT.md SUBMISSION_PACKET.md SETUP.md ./

ENV PYTHONPATH=/app/backend
CMD ["sh", "-c", "uvicorn prizepilot.main:app --host 0.0.0.0 --port ${PORT}"]

