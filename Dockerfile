FROM python:3.10-slim
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    cron \
    bash \
    && wget https://install.python-poetry.org -O get-poetry.py \
    && python get-poetry.py \
    && rm get-poetry.py

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY . .

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the crontab file to the cron.d directory
COPY cron /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron

# Apply cron job
RUN crontab /etc/cron.d/mycron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Ensure the wrapper script is executable
RUN chmod +x /app/run.sh


CMD cron -f
