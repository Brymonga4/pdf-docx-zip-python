FROM python:3.9

RUN apt-get update && apt-get install -y make

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

#CMD ["python", "./app.py"]
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "app:app"]