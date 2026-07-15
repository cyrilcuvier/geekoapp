FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sage_service ./sage_service

EXPOSE 9000
ENV GEEKO_SAGE_FLAG_PATH=/etc/geeko-sage/patched
CMD ["uvicorn", "sage_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
