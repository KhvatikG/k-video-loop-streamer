import os
import sys
from pathlib import Path
from loguru import logger


class AppConfig:
    def __init__(self):
        self.base_dir = self._get_base_dir()
        self.dirs = {
            'videos': self.base_dir / 'videos',
            'logs': self.base_dir / 'logs'
        }
        self.playlist_path = self.base_dir / 'loop_playlist.m3u'

    def _get_base_dir(self) -> Path:
        """Определение базовой директории для EXE и разработки"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent.parent

    def setup_dirs(self) -> None:
        """Создание рабочих директорий"""
        for d in self.dirs.values():
            d.mkdir(exist_ok=True)
        logger.info("Директории инициализированы")

    def get_vlc_path(self) -> Path:
        """Поиск VLC в системе"""
        paths = [
            Path(os.environ['ProgramFiles']) / 'VideoLAN' / 'VLC' / 'vlc.exe',
            Path.home() / 'AppData' / 'Roaming' / 'VLC' / 'vlc.exe'
        ]
        for p in paths:
            if p.exists():
                return p
        raise FileNotFoundError("VLC не найден")
