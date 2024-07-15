import ftplib
import os
import shutil
import time
import xml.etree.ElementTree as ET
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
FTP_HOST = "localhost"
FTP_USER = "user"
FTP_PASS = "password"
TEMP_FOLDER = "./temp"
LOCAL_FOLDER = "./local"
TRASH_FOLDER = "./trash"

# Ensure directories exist
for folder in [TEMP_FOLDER, LOCAL_FOLDER, TRASH_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Download files from FTP server
def download_files_from_ftp():
    with ftplib.FTP(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd("/home/user")
        filenames = ftp.nlst()
        
        for filename in filenames:
            local_temp_path = os.path.join(TEMP_FOLDER, filename)
            with open(local_temp_path, "wb") as file:
                ftp.retrbinary(f"RETR {filename}", file.write)
            
            # Move to the local folder after download completes
            local_final_path = os.path.join(LOCAL_FOLDER, filename)
            shutil.move(local_temp_path, local_final_path)

# Process the XML file
def process_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data_dict = {child.tag: child.text for child in root}
    print(data_dict)
    move_to_trash(file_path)

# Move processed file to trash
def move_to_trash(file_path):
    filename = os.path.basename(file_path)
    trash_path = os.path.join(TRASH_FOLDER, filename)
    shutil.move(file_path, trash_path)

# Watchdog event handler
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        process_file(event.src_path)

# Monitor the local folder for new files
def monitor_local_folder(folder):
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Main function to run the script
if __name__ == "__main__":
    download_files_from_ftp()
    monitor_local_folder(LOCAL_FOLDER)
