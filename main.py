import threading
import time
import subprocess

from app.api.api_main import on_startup
from app.logging_config import get_logger

logging = get_logger()

#starts the api puller and whatnot
def fetch_and_update_data():
    logging.info('Starting main process')
    on_startup()

#starts the strlt dashboard
def run_dashboard():
    logging.info("[Dashboard] Starting Streamlit app...")
    subprocess.run(["streamlit", "run", "app/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"])


#starts both threads
if __name__ == "__main__":
    logging.info('Starting main.py')
    t1 = threading.Thread(target=fetch_and_update_data)
    #strl dashboard commented out for now cause its not done yet, but it works :)
    #t2 = threading.Thread(target=run_dashboard)

    t1.start()
    #t2.start()

    t1.join()
    #t2.join()