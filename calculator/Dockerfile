FROM python:3.9-slim

COPY . /app/calculator

WORKDIR /app/calculator

EXPOSE 4060

RUN pip3 install --upgrade pip && \
pip3 install -r requirements.txt

WORKDIR /app

CMD ["uvicorn", "calculator.main:app", "--reload", "--host", "0.0.0.0", "--port", "4060"]
