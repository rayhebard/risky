FROM python:3.9-slim-buster

COPY . /app

WORKDIR /app

EXPOSE 8020

RUN pip3 install --upgrade pip && \
pip3 install -r requirements.txt

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8020"]
