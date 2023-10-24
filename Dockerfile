FROM python:3.10-slim
WORKDIR .
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . osint_military_api
CMD ["python3", "osint_military_api/main.py"]