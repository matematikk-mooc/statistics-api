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
RUN chown -R www-data:www-data /app && \
    find /app -type d -exec chmod 750 {} \; && \
    find /app -type f -exec chmod 640 {} \;

##############################################################
# Startup
##############################################################

WORKDIR /app
USER www-data
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_CACHE_DIR /app/.cache/pip
ENV PYTHONUSERBASE /app/.cache/.local
ENV PATH="${PYTHONUSERBASE}/bin:${PATH}"

EXPOSE 8000
ENTRYPOINT ["/app/.docker/startup.sh"]
