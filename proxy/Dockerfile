FROM python:3.13.0rc1-bookworm

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --verbose

COPY . .

EXPOSE 8080
CMD ["python", "app.py", "runserver", "0.0.0.0:8080"]
