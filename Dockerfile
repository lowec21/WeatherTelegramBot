FROM python:3.10
RUN mkdir "/app"
COPY requirements.txt /app/
COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/
CMD ["python", "-m", "main"]
