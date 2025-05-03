from watchdog.events import FileSystemEventHandler
from loguru import logger


class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event('modified', event)

    def on_created(self, event):
        self._handle_event('created', event)

    def on_deleted(self, event):
        self._handle_event('deleted', event)

    def _handle_event(self, event_type, event):
        logger.info(f"File {event_type}: {event.src_path}")
        self.callback()
