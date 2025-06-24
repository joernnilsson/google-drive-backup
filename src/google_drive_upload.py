# requirements: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import sys
from datetime import datetime

# Define the scopes
# TODO reduce scope
SCOPES = ['https://www.googleapis.com/auth/drive']

def service_account_login(creds_file):
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES)
    return creds

def get_service(creds_file):
    creds = service_account_login(creds_file)
    service = build('drive', 'v3', credentials=creds)
    return service

def list_files_in_folder(service, folder_id, page_size=100):
    """
    List all files in a Google Drive folder with their sizes.
    Uses paging to handle large numbers of files.
    
    Args:
        service: Google Drive service object
        folder_id: ID of the Google Drive folder
        page_size: Number of files to retrieve per page (max 1000)
    
    Returns:
        List of dictionaries containing file information
    """
    files = []
    page_token = None
    
    while True:
        try:
            # Query files in the specified folder
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = service.files().list(
                q=query,
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, size, mimeType, createdTime, modifiedTime)"
            ).execute()
            
            # Add files from current page to our list
            page_files = results.get('files', [])
            files.extend(page_files)
            
            # Get the next page token
            page_token = results.get('nextPageToken', None)
            
            # If no more pages, break the loop
            if not page_token:
                break
                
        except Exception as e:
            print(f"Error listing files: {e}")
            break
    
    return files

def print_files_summary(files):
    """
    Print a summary of files with their sizes in a readable format.
    
    Args:
        files: List of file dictionaries from list_files_in_folder
    """
    if not files:
        print("No files found in the folder.")
        return
    
    total_size = 0
    total_files = len(files)
    
    print(f"\nFound {total_files} files in the folder:")
    print("-" * 80)
    print(f"{'Name':<40} {'Size':<15} {'Type':<20} {'Modified':<20}")
    print("-" * 80)
    
    for file in files:
        name = file.get('name', 'Unknown')
        size = file.get('size', '0')
        mime_type = file.get('mimeType', 'Unknown')
        modified_time = file.get('modifiedTime', 'Unknown')
        
        # Convert size to human readable format
        if size != '0':
            size_int = int(size)
            total_size += size_int
            size_str = format_file_size(size_int)
        else:
            size_str = '0 B'
        
        # Truncate name if too long
        if len(name) > 38:
            name = name[:35] + "..."
        
        print(f"{name:<40} {size_str:<15} {mime_type:<20} {modified_time[:19]:<20}")
    
    print("-" * 80)
    print(f"Total files: {total_files}")
    print(f"Total size: {format_file_size(total_size)}")

def format_file_size(size_bytes):
    """
    Convert bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def delete_file(service, file_id, file_name):
    """
    Delete a file from Google Drive.
    
    Args:
        service: Google Drive service object
        file_id: ID of the file to delete
        file_name: Name of the file (for logging purposes)
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"Deleted file: {file_name} (ID: {file_id})")
        return True
    except Exception as e:
        print(f"Error deleting file {file_name} (ID: {file_id}): {e}")
        return False

def delete_old_backups(service, generational, folder_id, max_keep_daily_backups, max_keep_generational_backups):
    """
    Delete old backup files based on generational or daily backup strategy.
    
    Args:
        service: Google Drive service object
        generational: Boolean indicating if this is a generational backup strategy
        folder_id: ID of the Google Drive folder
        max_keep_daily_backups: Maximum number of daily backups to keep
        max_keep_generational_backups: Maximum number of generational backups to keep
    """
    files = list_files_in_folder(service, folder_id)
    
    if not files:
        print("No files found in the folder.")
        return
    
    print("All files in folder:")
    print_files_summary(files)
    
    # Filter files based on backup type
    if generational:
        # For generational backups, filter files that contain 'generational' in the name
        backup_files = [f for f in files if 'generational' in f.get('name', '').lower()]
        max_keep = max_keep_generational_backups
        backup_type = "generational"
    else:
        # For daily backups, filter files that don't contain 'generational' in the name
        backup_files = [f for f in files if 'generational' not in f.get('name', '').lower()]
        max_keep = max_keep_daily_backups
        backup_type = "daily"
    
    print(f"\nFound {len(backup_files)} {backup_type} backup files:")
    if backup_files:
        print_files_summary(backup_files)
    
    # If we have more files than the maximum allowed, delete the oldest ones
    if len(backup_files) > max_keep:
        # Sort files by modified time (oldest first)
        backup_files.sort(key=lambda x: x.get('modifiedTime', ''))
        
        # Calculate how many files to delete
        files_to_delete = len(backup_files) - max_keep
        files_to_remove = backup_files[:files_to_delete]
        
        print(f"\nNeed to delete {files_to_delete} old {backup_type} backup files to keep maximum of {max_keep}:")
        
        deleted_count = 0
        for file in files_to_remove:
            file_id = file.get('id')
            file_name = file.get('name', 'Unknown')
            if delete_file(service, file_id, file_name):
                deleted_count += 1
        
        print(f"Successfully deleted {deleted_count} out of {files_to_delete} old {backup_type} backup files.")
    else:
        print(f"No {backup_type} backup files need to be deleted. Current count: {len(backup_files)}, Max allowed: {max_keep}")

def upload_file(service, file_name, file_path, folder_id):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]  # Folder ID of the Google Drive folder
    }
    media = MediaFileUpload(file_path, mimetype='application/zip')

    print(f"google-drive > starting upload")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"google-drive > uploaded with id: {file.get('id')}")

def main():
    if len(sys.argv) < 3:
        print("usage: upload.py service_account.json driver_foler_id [file_name.tgz]")
        print("       upload.py service_account.json driver_foler_id --list")
        return
    
    service = get_service(sys.argv[1])
    folder_id = sys.argv[2]
    
    if len(sys.argv) == 3 or (len(sys.argv) == 4 and sys.argv[3] == '--list'):
        # List files mode
        print(f"Listing files in folder: {folder_id}")
        files = list_files_in_folder(service, folder_id)
        print_files_summary(files)
    elif len(sys.argv) == 4:
        # Upload mode
        file_path = sys.argv[3]
        upload_file(service, os.path.basename(file_path), file_path, folder_id)
    else:
        print("Invalid arguments. Use --list to list files or provide a file path to upload.")

if __name__ == '__main__':
    main()


