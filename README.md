# Google Play to Looker Studio Importer

This project provides a Python-based solution to download Google Play store installation data from a Google Cloud Storage bucket, process it, and upload the results to a Google Sheet, making it accessible for further analysis in Looker Studio. The code as it exists right now just imports Install metrics into a Google Sheet, however this example can be easily expanded to handle other metrics published in Google Play nightly CSV files such as revenue, subscription, churn and crash metrics.

## Key Features
- **Google Cloud Integration**: Downloads installation data stored in Google Cloud Storage.
- **Google Sheets Integration**: Processes the downloaded data and updates a Google Sheet with the latest information.
- **Dockerized Environment**: The entire process is containerized using Docker, ensuring easy deployment and environment consistency.

## Prerequisites
Before building and running the Docker container, ensure that you have the following:
- A Google Cloud Service Account with appropriate permissions. Please ensure these credentials are in json format in a file named "google-credentials.json" that sits in the directory that you map to the /app/data path in the Docker container.
- Access to the Google Cloud Storage bucket containing the Google Play Account data. Please see the associated blog post for instructions on where to find this.
- A Google Sheet set up to receive the processed data.
- Docker installed on your machine.

## Environment Variables
The following environment variables need to be set up for the script to run correctly. Place a .env file inside the folder mapped to the /app/data path for your Docker container.:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account credentials file.
- `PLAY_STORE_BUCKET_NAME`: Name of the Google Cloud Storage bucket.
- `SPREADSHEET_ID`: ID of the Google Sheet where data will be uploaded.
- `INSTALLS_WORKSHEET_NAME`: Name of the worksheet within the Google Sheet to update.
- `START_DATE`: Start date to fetch data from (in `YYYY-MM-DD` format).
- `DAYS_TO_FETCH_INSTALLS_FOR`: Number of days prior to today for which to fetch installation data.

## Running the Code Locally on Your Machine
To build and run this code on your local dev machine and outside of a docker containter first install the dependencies using Poetry:
```bash
poetry install
```
Once that completes, then modify these lines of code to point to directories on your local machine and place the google-credentials.json and .env files within it:
```bash
credentials_path = "/app/data/google-credentials.json"
download_folder = "/app/data/installs/"
```
Ensure that you have set all enviornment variables within your shell environment to match those that are specified above. 

## Building the Docker Image

To build the Docker image, navigate to the directory containing the Dockerfile and run:

```bash
docker build -t google-play-to-looker-studio-importer .
```

## Running the Docker Container

Once the Docker image is built, you can run the container with the following command:
```bash
docker run -d --restart unless-stopped --name google-play-to-looker-studio-importer -v /path/to/local/data:/app/data  google-play-to-looker-studio-importer
```
Once started, a cron job within the Docker container will run every 15 minutes and process newly published CSV data in your Google Cloud Storage bucket and update the associated Google Sheet with the latest install metrics.