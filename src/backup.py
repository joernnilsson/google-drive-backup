import os
import zipfile
from datetime import datetime
import argparse

def make_zip_filename(output_directory, timestamp, is_generational):
    # Generate a timestamp
    timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
    postfix = "_generational" if is_generational else f""
    zip_filename = f"backup_{timestamp_str}{postfix}.zip"
    zip_filepath = os.path.join(output_directory, zip_filename)
    return zip_filepath

def zip_folders(folder_paths, zip_filepath):

    # Create a zip file
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_path in folder_paths:
            print(f"backup > adding {folder_path}")
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # Create a proper path for each file to be zipped
                    file_path = os.path.join(root, file)
                    # Write the file to the zip file, with the path relative to the folder being zipped
                    arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                    zipf.write(file_path, arcname)

    file_size = os.stat(zip_filepath).st_size
    print(f"backup > created {zip_filepath} (size: {file_size})")
    return zip_filepath


def main():
    description = 'Create backup zip file of specified folders'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--item', '-i', action='store', dest='items',
                        type=str, nargs='*', default=[],
                        help="Examples: -i item1 item2 -i item3")
    parser.add_argument('--output-file', '-o', type=str, help='Output zip file', default=None)
    opts = parser.parse_args()

    zip_filename = zip_folders(opts.items, opts.output_file if opts.output_file else make_zip_filename("/tmp"))
    print(f"Backup created at {zip_filename}")
    pass
    

if __name__ == '__main__':
    main()