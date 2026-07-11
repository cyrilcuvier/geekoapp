FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY oracle_service ./oracle_service

EXPOSE 9000
ENV GEEKO_ORACLE_FLAG_PATH=/etc/geeko-oracle/patched
CMD ["uvicorn", "oracle_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
