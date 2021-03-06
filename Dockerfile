FROM ubuntu:18.04
COPY requirements.txt /requirements.txt
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser && apt update && apt install openssh-server python3 python3-pip python3-venv libmysqlclient-dev gdal-bin gosu -y && echo "root:Docker!" | chpasswd && /usr/bin/python3 -m venv /app/venv && /app/venv/bin/python3 -m pip install -r /requirements.txt
COPY sshd_config sshd_setup.sh /etc/ssh/
COPY manage.py start_web_app.sh entrypoint.sh ca.crt /app/
COPY statistics_api /app/statistics_api/
WORKDIR /app/
RUN chown appuser:appuser -R /app && chmod 700 /etc/ssh/sshd_setup.sh && /etc/ssh/sshd_setup.sh && find . -type d | grep -v "./venv" | xargs chmod 755 && find . -type f | grep -v "./venv" | xargs chmod 644 && chmod 700 entrypoint.sh start_web_app.sh
ENV PYTHONPATH="/app"
# If you use a non-default value for WEBSITES_PORT, you must change the corresponding variable in Azure app configuration settings upon deployment
ARG WEBSITES_PORT=8000
EXPOSE "${WEBSITES_PORT}" 2222
CMD ["./entrypoint.sh"]
