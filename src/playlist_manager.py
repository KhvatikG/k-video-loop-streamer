from datetime import datetime
from loguru import logger


class PlaylistGenerator:
    def __init__(self, config):
        self.config = config
        self.last_update = None
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov'}

    def generate_playlist(self) -> bool:
        """Генерация плейлиста с поддержкой Unicode и проверкой наличия файлов"""
        try:
            video_files = [
                file for file in sorted(self.config.dirs['videos'].iterdir())
                if file.is_file() and file.suffix.lower() in self.video_extensions
            ]

            # Проверка наличия видеофайлов
            if not video_files:
                logger.warning("Не найдено видеофайлов в директории videos. Создан пустой плейлист.")

            with open(self.config.playlist_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n#EXTVLCOPT:repeat\n")
                for file in video_files:
                    # Преобразуем путь в URI формат совместимый с Windows
                    file_uri = file.resolve().as_uri()
                    f.write(f"{file_uri}\n")

            self.last_update = datetime.now()
            logger.info(f"Плейлист обновлен: {len(video_files)} файлов")
            return True
        except Exception as e:
            logger.error(f"Playlist error: {str(e)}")
            return False
