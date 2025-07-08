FROM python:3.13.0-slim

ENV USER=alex-user \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash $USER

ENV APP_DIR=/home/$USER/src

WORKDIR $APP_DIR

COPY src/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src $APP_DIR

ENV PYTHONPATH=$APP_DIR

RUN chown -R "$USER":"$USER" $APP_DIR
USER $USER

