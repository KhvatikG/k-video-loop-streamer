import json
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
        self.config_path = self.base_dir / 'config.json'

        # Параметры по умолчанию
        self.settings = {
            'http_port': 8080,
            'video_extensions': ['.mp4', '.avi', '.mkv', '.mov'],
            'vlc_custom_path': None
        }

        # Загружаем пользовательские настройки, если есть
        self._load_config()

    def _get_base_dir(self) -> Path:
        """Определение базовой директории для EXE и разработки"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent.parent

    def _load_config(self):
        """Загрузка пользовательских настроек"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.settings.update(user_config)
                logger.info("Загружены пользовательские настройки")
            else:
                # Создаем файл настроек по умолчанию
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=4, ensure_ascii=False)
                logger.info("Создан файл настроек по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")

    def setup_dirs(self) -> None:
        """Создание рабочих директорий"""
        for d in self.dirs.values():
            d.mkdir(exist_ok=True)
        logger.info("Директории инициализированы")

    def get_vlc_path(self) -> Path:
        """Расширенный поиск VLC в системе"""
        # Если пользователь указал путь в настройках
        if self.settings['vlc_custom_path'] and Path(self.settings['vlc_custom_path']).exists():
            return Path(self.settings['vlc_custom_path'])

        # Стандартные пути установки
        standard_paths = [
            Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'VideoLAN' / 'VLC' / 'vlc.exe',
            Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'VideoLAN' / 'VLC' / 'vlc.exe',
            Path.home() / 'AppData' / 'Local' / 'Programs' / 'VideoLAN' / 'VLC' / 'vlc.exe',
            Path.home() / 'AppData' / 'Roaming' / 'VLC' / 'vlc.exe'
        ]

        # Поиск через переменную PATH
        if 'PATH' in os.environ:
            for path_entry in os.environ['PATH'].split(os.pathsep):
                potential_path = Path(path_entry) / 'vlc.exe'
                if potential_path.exists():
                    return potential_path

        # Проверка стандартных путей
        for p in standard_paths:
            if p.exists():
                return p

        raise FileNotFoundError("VLC не найден. Укажите путь в config.json (vlc_custom_path)")
