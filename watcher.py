# filepath: /Users/amandawu/CS/cs150/LLMProxy/watcher.py
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        self.process = os.popen(self.command)

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}. Restarting server...")
            self.start_process()

if __name__ == "__main__":
    command = "python3 server.py"
    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    print("Watching for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()