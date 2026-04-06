FROM python:3.13-slim

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh && \
    chown -R appuser:appgroup /app

ENV FLASK_APP=app
ARG FLASK_ENV=production
ENV FLASK_ENV=${FLASK_ENV}

USER appuser

EXPOSE 5000

CMD ["./entrypoint.sh"]