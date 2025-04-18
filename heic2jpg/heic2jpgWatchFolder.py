import os
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import pillow_heif
import time

class HEICWatcher(FileSystemEventHandler):
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        pillow_heif.register_heif_opener()

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"File created: {file_path}")
        if file_path.lower().endswith('.heic'):
            self.convert_heic_to_jpg(file_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"File deleted: {file_path}")
        if file_path.lower().endswith('.heic'):
            self.delete_corresponding_jpg(file_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        old_path = event.src_path
        new_path = event.dest_path
        print(f"File moved: {old_path} -> {new_path}")
        if old_path.lower().endswith('.heic'):
            self.delete_corresponding_jpg(old_path)

        if new_path.lower().endswith('.heic'):
            self.convert_heic_to_jpg(new_path)

    def convert_heic_to_jpg(self, heic_path):
        file_name, file_ext = os.path.splitext(heic_path)
        jpg_path = f"{file_name}_converted.jpg"
        if not os.path.exists(jpg_path):
            try:
                if pillow_heif.is_supported(heic_path):
                    im = Image.open(heic_path)
                    icc_profile = im.info.get('icc_profile')
                    im.save(jpg_path, "JPEG", quality=90, icc_profile=icc_profile)
                    print(f"Converted {heic_path} to {jpg_path}")
            except Exception as e:
                print(f"Error converting {heic_path}: {e}")
        else:
            print(f"Skipped: {jpg_path} already exists.")

    def delete_corresponding_jpg(self, heic_path):
        file_name, file_ext = os.path.splitext(heic_path)
        jpg_path = f"{file_name}_converted.jpg"
        if os.path.exists(jpg_path):
            try:
                os.remove(jpg_path)
                print(f"Deleted {jpg_path}")
            except Exception as e:
                print(f"Error deleting {jpg_path}: {e}")

def start_watching(watch_dir):
    event_handler = HEICWatcher(watch_dir)
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=True)
    observer.start()
    print(f"Watching folder: {watch_dir}")

    def stop_observer(signum, frame):
        observer.stop()
        observer.join()
        print("Stopping folder watcher with signal...")
        sys.exit(1)

    signal.signal(signal.SIGTERM, stop_observer)
    signal.signal(signal.SIGINT, stop_observer)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Stopping folder watcher...")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python heic2jpgWatchFolder.py <watch_folder>")
        sys.exit(1)

    watch_folder = sys.argv[1]
    start_watching(watch_folder)
