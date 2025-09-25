import sys
import os
import subprocess
import time
import atexit
import logging
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import QApplication, QMessageBox
from dashboard.main_window import MainWindow
from rfq_tracker.db_manager import DBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
MONGO_VERSION = "7.0.5"
MONGO_URL = f"https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-{MONGO_VERSION}.zip"
VENDOR_DIR = "" # Will be set in main()
MONGO_EXECUTABLE = "" # Will be set in main()

# Global variable to hold the MongoDB process
mongo_process = None

def get_vendor_path(is_frozen: bool) -> str:
    """Gets the path to the vendor directory, handling frozen (PyInstaller) and normal script execution."""
    if is_frozen:
        return os.path.join(os.path.dirname(sys.executable), 'vendor')
    else:
        return os.path.join(os.path.dirname(__file__), 'vendor')

def show_error_message(text: str, informative_text: str = ""):
    """Displays a critical error message box and exits the application."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText(text)
    msg_box.setInformativeText(informative_text)
    msg_box.setWindowTitle("Application Error")
    msg_box.exec()
    sys.exit(1)

def download_and_extract_mongodb(vendor_path: str):
    """Downloads and extracts MongoDB if it's not found."""
    mongo_zip_path = os.path.join(vendor_path, 'mongodb.zip')
    mongo_extract_path = os.path.join(vendor_path, 'mongodb_temp')
    final_mongo_path = os.path.join(vendor_path, 'mongodb')

    logging.info("MongoDB not found. Starting download...")
    # In a real app, you would show a progress dialog here.
    # For this example, we'll just log to console.
    try:
        with requests.get(MONGO_URL, stream=True) as r:
            r.raise_for_status()
            with open(mongo_zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info("Download complete. Extracting...")

        with zipfile.ZipFile(mongo_zip_path, 'r') as zip_ref:
            zip_ref.extractall(mongo_extract_path)

        # The files are in a nested folder, e.g., mongodb-windows-x86_64-7.0.5
        # We need to move them up.
        extracted_folder_name = os.listdir(mongo_extract_path)[0]
        source_dir = os.path.join(mongo_extract_path, extracted_folder_name)

        # Move contents to the final destination
        shutil.move(source_dir, final_mongo_path)

        logging.info("Extraction complete.")

    except Exception as e:
        logging.error(f"Failed to download or extract MongoDB: {e}")
        show_error_message("Failed to download required components.", f"Error: {e}")
    finally:
        # Clean up
        if os.path.exists(mongo_zip_path):
            os.remove(mongo_zip_path)
        if os.path.exists(mongo_extract_path):
            shutil.rmtree(mongo_extract_path)


def start_mongodb():
    """Starts the bundled MongoDB server, downloading it if necessary."""
    global mongo_process

    if not os.path.exists(MONGO_EXECUTABLE):
        download_and_extract_mongodb(VENDOR_DIR)

    if not os.path.exists(MONGO_EXECUTABLE):
        logging.error(f"MongoDB executable still not found after download attempt at: {MONGO_EXECUTABLE}")
        show_error_message("Could not locate the MongoDB executable.", "The application cannot continue without the database engine.")
        sys.exit(1)

    db_path = os.path.join(VENDOR_DIR, 'mongodb', 'data')
    log_path = os.path.join(VENDOR_DIR, 'mongodb', 'log', 'mongod.log')
    os.makedirs(db_path, exist_ok=True)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.info(f"Starting MongoDB from: {MONGO_EXECUTABLE}")
    try:
        mongo_process = subprocess.Popen([MONGO_EXECUTABLE, '--dbpath', db_path, '--logpath', log_path, '--port', '27017'])
        logging.info(f"MongoDB started with PID: {mongo_process.pid}")
        time.sleep(3)
    except Exception as e:
        logging.error(f"Failed to start MongoDB: {e}")
        show_error_message("Failed to start the local database.", f"Error: {e}")
        sys.exit(1)

def stop_mongodb():
    """Stops the MongoDB server if it's running."""
    global mongo_process
    if mongo_process:
        logging.info("Stopping MongoDB...")
        mongo_process.terminate()
        mongo_process.wait()
        logging.info("MongoDB stopped.")

def main():
    """
    Main entry point for the RFQ Tracker application.
    """
    global VENDOR_DIR, MONGO_EXECUTABLE

    # This needs to be done once, at the start.
    app = QApplication(sys.argv)

    is_frozen = getattr(sys, 'frozen', False)
    VENDOR_DIR = get_vendor_path(is_frozen)
    MONGO_EXECUTABLE = os.path.join(VENDOR_DIR, 'mongodb', 'bin', 'mongod.exe')

    os.makedirs(VENDOR_DIR, exist_ok=True)

    start_mongodb()
    atexit.register(stop_mongodb)

    try:
        db_manager = DBManager(uri="mongodb://localhost:27017")
    except Exception as e:
        logging.error(f"Could not connect to the database: {e}")
        show_error_message("Could not connect to the local database.", f"Error: {e}")
        sys.exit(1)

    window = MainWindow(db_manager=db_manager)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()