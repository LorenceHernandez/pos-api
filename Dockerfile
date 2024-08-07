FROM python:3.13.0rc1-bookworm

RUN pip install --upgrade pip
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py", "runserver", "0.0.0.0:5000"]
