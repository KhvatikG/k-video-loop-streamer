from datetime import datetime
from loguru import logger


class PlaylistGenerator:
    def __init__(self, config):
        self.config = config
        self.last_update = None

    def generate_playlist(self) -> bool:
        """Генерация плейлиста с поддержкой Unicode"""
        try:
            with open(self.config.playlist_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n#EXTVLCOPT:repeat\n")
                for file in sorted(self.config.dirs['videos'].iterdir()):
                    if file.suffix.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
                        f.write(f"{file.resolve().as_posix()}\n")
            self.last_update = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Playlist error: {str(e)}")
            return False
