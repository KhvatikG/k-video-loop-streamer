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
            logger.error("Ошибка создания плейлиста")
            return

        # Запуск VLC
        playlist_uri = config.playlist_path.resolve().as_uri()  # Корректный URI формат
        if not vlc.start(playlist_uri):
            logger.error("Не удалось запустить VLC")
            return

        # Мониторинг файлов
        observer = Observer()
        event_handler = VideoFileHandler(playlist.generate_playlist)
        observer.schedule(event_handler, path=str(config.dirs['videos']), recursive=False)
        observer.start()

        logger.info("Приложение запущено")

        # Основной цикл с проверкой состояния VLC
        try:
            while True:
                if not vlc.is_running():
                    logger.warning("VLC не запущен, перезапуск...")
                    vlc.restart(playlist_uri)
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        # Корректное завершение работы
        try:
            observer.stop()
            observer.join(timeout=5)
        except Exception as e:
            logger.error(f"Ошибка при остановке Observer: {e}")

        vlc.stop()
        logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
