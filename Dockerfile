FROM python:3.12.2

########            SYSTEM          #########

# Create app user
RUN groupadd -g 999 appuser
RUN useradd -r -u 999 -g appuser appuser
RUN echo "root:Docker!" | chpasswd

# Install packages
RUN apt-get update &&  \
    apt-get install -y  openssh-server \
                        python3-pip \
                        python3-venv \
                        libmariadb-dev \
                        gdal-bin \
                        gosu \
                        python3-dev \
                        default-libmysqlclient-dev \
                        build-essential \
                        pkg-config

# Set virtual environment
RUN /usr/bin/python3 -m venv /app/venv



########            APP          #########
# Copy app files
COPY requirements.txt /requirements.txt
COPY sshd_config sshd_setup.sh /etc/ssh/
COPY manage.py start_web_app.sh entrypoint.sh ca.crt /app/
COPY statistics_api /app/statistics_api/

WORKDIR /app/

# Install python requirements
RUN /app/venv/bin/python3 -m pip install -r /requirements.txt --default-timeout=100

# Setup ssh
RUN chmod 700 /etc/ssh/sshd_setup.sh
RUN /etc/ssh/sshd_setup.sh

# File premissions, app
RUN chown appuser:appuser -R /app
RUN find . -type d | grep -v "./venv" | xargs chmod 755
RUN find . -type f | grep -v "./venv" | xargs chmod 644
RUN chmod 700 entrypoint.sh start_web_app.sh

ENV PYTHONPATH="/app"
ARG WEBSITES_PORT=8000

########        START APP     #########
EXPOSE "${WEBSITES_PORT}" 2222
CMD ["./entrypoint.sh"]
