FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app
ARG FLASK_ENV=production
ENV FLASK_ENV=${FLASK_ENV}

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]