import threading
import time
import subprocess
from app.logging_config import get_logger

logging = get_logger()

def fetch_and_update_data():
    while True:
        logging.info("[Fetcher] Pulling data from API...")
        # Do API calls, update database
        time.sleep(1)  # Simulate waiting time

def run_dashboard():
    logging.info("[Dashboard] Starting Streamlit app...")
    subprocess.run(["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    t1 = threading.Thread(target=fetch_and_update_data)
    t2 = threading.Thread(target=run_dashboard)

    t1.start()
    t2.start()

    t1.join()
    t2.join()