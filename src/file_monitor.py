from watchdog.events import FileSystemEventHandler
from loguru import logger


class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov'}

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event('modified', event)

    def on_created(self, event):
        if not event.is_directory:
            self._handle_event('created', event)

    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_event('deleted', event)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle_event('moved', event)

    def _handle_event(self, event_type, event):
        path = getattr(event, 'src_path', None)
        # Проверяем, является ли файл видео
        if path and any(path.lower().endswith(ext) for ext in self.video_extensions):
            logger.info(f"Видеофайл {event_type}: {path}")
            self.callback()
        else:
            logger.debug(f"Событие {event_type} для не-видео файла: {path}")
