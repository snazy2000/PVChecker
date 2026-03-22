FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY PVChecker.py /app/PVChecker.py
COPY pv /app/pv

CMD ["python", "-u","PVChecker.py"]
