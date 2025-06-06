FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN apt-get update && apt-get install -y dos2unix && \
    find . -type f -name "*.sh" -exec dos2unix {} +
RUN chmod +x wait-for-it.sh

CMD ["sh", "-c", "./wait-for-it.sh db:5432 -- python populate_vectors.py && uvicorn api:app --host 0.0.0.0 --port 8000"] 