import argparse
import yaml
import os
import schedule
import requests
import time
from datetime import datetime

import backup
import google_drive_upload

def timestamp_is_generational(timestamp):
    return timestamp.day == 1


def job(config, opts):

    timestamp = datetime.now()
    generational = timestamp_is_generational(timestamp)
    
    # Create backup archive
    zip_file = backup.zip_folders(opts.items, backup.make_zip_filename("/tmp", timestamp, generational))

    # Upload to google drive
    service = google_drive_upload.get_service(opts.google_drive_credentials_file)
    google_drive_upload.upload_file(service, os.path.basename(zip_file), zip_file, config["google_drvie_folder"])

    # Delete old backups
    google_drive_upload.delete_old_backups(service, generational, config["google_drvie_folder"],  config["max_keep_daily_backups"], config["max_keep_generational_backups"])

    # Cleanup
    os.remove(zip_file)

def wrapped_job(config, opts):

    try:
        job(config, opts)
        payload = {
            "title": f"{config['name']} backup succeeded",
            "message": ""
        }
        print(f"main > job succeeded")

    except Exception as e:
        payload = {
            "title": f"{config['name']} backup failed",
            "message": str(e)
        }
        print(f"main > job failed with message: {str(e)}")

    # Call webhook if configured
    if config.get('webhook'):
        response = requests.post(config['webhook'], json=payload)
        print(f"main > webhook responded with: {response.status_code}")
    else:
        print(f"main > no webhook configured, skipping notification")

def main():
    parser = argparse.ArgumentParser(description='Create backup and upload to Google Drive')
    parser.add_argument('--config-file', type=str, help='Config file', default=None, required=True)
    parser.add_argument('--google-drive-credentials-file', type=str, help='Google drive service account credentials', default=None, required=True)
    parser.add_argument('--item', '-i', action='store', dest='items', type=str, nargs='*', default=['/backup'])
    parser.add_argument('--schedule', action='store_true', default=False)
    parser.add_argument('--run-now', action='store_true', default=False)
    opts = parser.parse_args()

    with open(opts.config_file) as stream:
        config = yaml.safe_load(stream)

    # Set default values for configuration parameters
    config.setdefault('schedule', '00:00')
    config.setdefault('max_keep_daily_backups', 10)
    config.setdefault('max_keep_generational_backups', 10)
    config.setdefault('webhook', None)

    if opts.run_now:
        wrapped_job(config, opts)

    if opts.schedule:
        print(f"scheduler > scheduling backup every day at: {config['schedule']}")
        schedule.every().day.at(config['schedule']).do(wrapped_job, config=config, opts=opts)
        while 1:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    main()