FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY geeko_api ./geeko_api

EXPOSE 8000
ENV REDIS_URL=redis://redis:6379/0
CMD ["uvicorn", "geeko_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
