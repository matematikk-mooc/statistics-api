FROM ubuntu:18.04
COPY requirements.txt /requirements.txt
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser && apt update && apt install python3 python3-pip python3-venv libmysqlclient-dev -y && /usr/bin/python3 -m venv /app/venv && /app/venv/bin/python3 -m pip install -r /requirements.txt
COPY manage.py entrypoint.sh ca.crt wait-for-it.sh /app/
COPY statistics_api /app/statistics_api/
RUN chmod 700 /app/entrypoint.sh && chown appuser:appuser /app/entrypoint.sh
USER appuser
WORKDIR /app/
ENV PYTHONPATH="/app"
CMD ["./entrypoint.sh"]
