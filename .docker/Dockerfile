FROM python:3.12.4

RUN apt-get update && apt-get install -y \
    nano \
    curl \
    supervisor \
    zip \
    unzip \
    openssh-server \
    default-mysql-client \
    libmariadb-dev \
    gdal-bin \
    gosu \
    python3-pip \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

##############################################################
# Startup
##############################################################

WORKDIR /app
USER root
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000
ENTRYPOINT ["/app/.docker/startup.sh"]
