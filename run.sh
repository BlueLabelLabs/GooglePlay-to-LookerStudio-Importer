#!/bin/bash
# Export the current environment variables to a file
#declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# Print the current working directory
echo "Current working directory at the start of run.sh: $(pwd)"

# Source the environment variables file to make them available to the cron job
# Enable automatic export of all variables
set -a

# Source the environment variables from the .env file
source /app/data/.env

# Disable automatic export of variables
set +a

# Run the main Python script using the correct Python interpreter
/usr/local/bin/python3 /app/main.py

/usr/local/bin/python3 /app/download_installs.py

/usr/local/bin/python3 /app/download_financials.py

/usr/local/bin/python3 /app/download_subscriptions.py

/usr/local/bin/python3 /app/pubsub_subscriber.py