FROM python:3.9-slim-buster

COPY . /app/data_domain

WORKDIR /app/data_domain

EXPOSE 6040

RUN pip3 install --upgrade pip && \
pip3 install -r requirements.txt

WORKDIR /app

CMD ["uvicorn", "data_domain.main:app", "--reload", "--host", "0.0.0.0", "--port", "6040"]
