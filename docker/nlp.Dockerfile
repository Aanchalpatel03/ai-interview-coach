FROM python:3.12-slim

WORKDIR /app

COPY ml-services/nlp-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ml-services/nlp-service /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8101"]
