import time
from watchdog.observers import Observer
from loguru import logger
from config import AppConfig
from playlist_manager import PlaylistGenerator
from file_monitor import VideoFileHandler
from vlc_runner import VLCController


def configure_logging(config):
    logger.add(
        config.dirs['logs'] / 'app_{time:YYYY-MM-DD}.log',
        rotation="00:00",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )


def main():
    config = AppConfig()
    config.setup_dirs()
    configure_logging(config)

    try:
        # Инициализация компонентов
        playlist = PlaylistGenerator(config)
        vlc = VLCController(config)

        # Первоначальная генерация плейлиста
        if not playlist.generate_playlist():
            raise RuntimeError("Ошибка создания плейлиста")

        # Запуск VLC
        playlist_uri = f"file:///{config.playlist_path.resolve().as_posix()}"
        if not vlc.start(playlist_uri):
            raise RuntimeError("Не удалось запустить VLC")

        # Мониторинг файлов
        observer = Observer()
        event_handler = VideoFileHandler(playlist.generate_playlist)
        observer.schedule(event_handler, path=str(config.dirs['videos']), recursive=False)
        observer.start()

        logger.info("Приложение запущено")
        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        observer.stop()
        observer.join()
        vlc.stop()
        logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
