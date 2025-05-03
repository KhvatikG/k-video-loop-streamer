import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger


class Config:
    def __init__(self):
        self.base_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
        self.video_dir = self.base_dir / "videos"
        self.playlist_path = self.base_dir / "loop_playlist.m3u"
        self.logs_dir = self.base_dir / "logs"

        self._setup_directories()
        self._configure_logging()

    def _setup_directories(self):
        self.video_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)

    def _configure_logging(self):
        logger.add(
            self.logs_dir / "videoloop_{time}.log",
            rotation="00:00",
            retention="7 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            enqueue=True,
            backtrace=False
        )
        logger.info("Application initialized")


class PlaylistManager:
    def __init__(self, config):
        self.config = config

    def generate_playlist(self):
        try:
            with open(self.config.playlist_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n#EXTVLCOPT:repeat\n")
                for file in sorted(self.config.video_dir.iterdir()):
                    if file.suffix.lower() in (".mp4", ".avi", ".mkv", ".mov"):
                        f.write(f"{file.resolve()}\n")
            logger.success("Playlist updated")
        except Exception as e:
            logger.error(f"Playlist generation failed: {str(e)}")


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_any_event(self, event):
        if not event.is_directory and event.event_type in ('created', 'deleted', 'modified'):
            logger.info(f"File event: {event.event_type} - {event.src_path}")
            self.manager.generate_playlist()


class VLCServer:
    def __init__(self, config):
        self.config = config
        self.vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

    def start(self):
        try:
            cmd = [
                self.vlc_path,
                "--loop",
                "--playlist-autostart",
                "--daemon",
                "--intf", "dummy",
                str(self.config.playlist_path)
            ]
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.success("VLC server started")
        except FileNotFoundError:
            logger.critical("VLC not found! Install from https://www.videolan.org/")
            sys.exit(1)


def main():
    config = Config()
    manager = PlaylistManager(config)
    manager.generate_playlist()

    # Инициализация VLC
    VLCServer(config).start()

    # Мониторинг файлов
    event_handler = FileEventHandler(manager)
    observer = Observer()
    observer.schedule(event_handler, path=str(config.video_dir), recursive=False)
    observer.start()
    logger.info("File monitoring started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Shutting down by user request")
    finally:
        observer.stop()
        observer.join()
        logger.info("Application stopped")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Critical error: {str(e)}")
        sys.exit(1)
