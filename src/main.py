import argparse
import yaml
import os

import backup
import google_drive_upload

def main():
    parser = argparse.ArgumentParser(description='Create backup and upload to Google Drive')
    parser.add_argument('--config-file', type=str, help='Config file', default=None, required=True)
    parser.add_argument('--google-drive-credentials-file', type=str, help='Google drive service account credentials', default=None, required=True)
    parser.add_argument('--item', '-i', action='store', dest='items', type=str, nargs='*', default=['/backup'])
    opts = parser.parse_args()

    with open(opts.config_file) as stream:
        config = yaml.safe_load(stream)

    # Create backup archive
    zip_file = backup.zip_folders(opts.items, backup.make_zip_filename("/tmp"))

    # Upload to google drive
    service = google_drive_upload.get_service(opts.google_drive_credentials_file)
    google_drive_upload.upload_file(service, os.path.basename(zip_file), zip_file, config["google_drvie_folder"])

    # Cleanup
    os.remove(zip_file)

if __name__ == '__main__':
    main()