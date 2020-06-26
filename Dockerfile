FROM ubuntu:18.04
COPY requirements.txt /requirements.txt
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser && apt update && apt install python3 python3-pip python3-venv libmysqlclient-dev gdal-bin -y && /usr/bin/python3 -m venv /app/venv && /app/venv/bin/python3 -m pip install -r /requirements.txt
COPY manage.py entrypoint.sh ca.crt /app/
COPY statistics_api /app/statistics_api/
RUN chown appuser:appuser -R /app
USER appuser
WORKDIR /app/
RUN find . -type d | grep -v "./venv" | xargs chmod 755 && find . -type f | grep -v "./venv" | xargs chmod 644 && chmod 700 entrypoint.sh
ENV PYTHONPATH="/app"
CMD ["./entrypoint.sh"]
