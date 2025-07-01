# Google Drive Backup Service

A Docker-based backup service that automatically backs up specified files and folders to Google Drive with configurable retention policies.

## Features

- **Automated backups**: Schedule regular backups of your important files
- **Google Drive integration**: Secure cloud storage using Google Drive API
- **Configurable retention**: Keep daily and generational backups with customizable limits
- **Docker-based**: Easy deployment and updates
- **Service account authentication**: Secure API access without user interaction
- **File listing and management**: View and manage backup files in Google Drive

## Quick Start

### Prerequisites

- Docker installed and running
- Google Cloud Platform account with Drive API enabled
- Service account with Google Drive permissions

### Installation

1. **Download the necessary files:**
   ```bash
   wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/install_update.sh
   wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/config_example.yaml -O config.yaml
   chmod +x install_update.sh
   ```

2. **Configure the backup service:**
   - Edit `config.yaml` to specify your backup items and settings
   - Add your `service_account.json` file to the directory

3. **Install and start the service:**
   ```bash
   ./install_update.sh
   ```

### Configuration

The `config.yaml` file allows you to configure:

- **Backup items**: Files and folders to backup
- **Google Drive folder**: Destination folder ID in Google Drive
- **Retention policies**: How many daily and generational backups to keep
- **Backup schedule**: When to run backups

Example configuration:
```yaml
name: "home-server"
schedule: "00:00"
google_drvie_folder: "1SN-3**********************w_1Eiv7y5BWop"
max_keep_daily_backups: 10
max_keep_generational_backups: 10
webhook: "https://example.com/api/webhook/-_Ucrg********PqhsCs"
items:
 - README.md
 - /home/file.txt
 - /home/directory
```

### Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create a service account
5. Download the JSON key file as `service_account.json`
6. Share your Google Drive folder with the service account email

### Google Drive folder

1. Create a folder to store the backups
2. Share it with write permissions with the service account email address

Note: Service accounts have their own storage quata of 5GB. Please do the math when selecting backup items and retention policy!

### Usage

#### Manual Backup
```bash
docker exec google-drive-backup python /app/main.py --config-file /config/config.yaml --google-drive-credentials-file /config/service_account.json --run-now
```

#### List Files in Google Drive
```bash
docker exec google-drive-backup python /app/src/google_drive_upload.py /config/service_account.json your_folder_id --list
```

#### Update the Service
```bash
./install_update.sh
```

### File Management

The service includes tools for managing backup files:

- **List all files**: View all backup files with sizes and dates
- **Automatic cleanup**: Remove old backups based on retention policies
- **Generational backups**: Keep important backups longer with different retention rules

### Troubleshooting

#### Common Issues

1. **Service account authentication failed**
   - Verify `service_account.json` is valid and has proper permissions
   - Ensure the Google Drive folder is shared with the service account

2. **Backup items not found**
   - Check that all paths in `config.yaml` exist and are accessible
   - Verify Docker volume mounts are working correctly

3. **Container won't start**
   - Check Docker logs: `docker logs google-drive-backup`
   - Verify all required files are present

#### Logs

View service logs:
```bash
docker logs google-drive-backup
```

Follow logs in real-time:
```bash
docker logs -f google-drive-backup
```

### Development

#### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/joernnilsson/google-drive-backup.git
   cd google-drive-backup
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Building the Docker Image

```bash
docker build -t google-drive-backup .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the configuration examples

### Quick one line installation
```bash
wget -qO-  https://github.com/joernnilsson/google-drive-backup/raw/refs/heads/master/bootstrap.sh | bash
```