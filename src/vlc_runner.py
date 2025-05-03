import subprocess
from loguru import logger


class VLCController:
    def __init__(self, config):
        self.config = config
        self.process = None

    def start(self, playlist_uri: str) -> bool:
        """Запуск VLC с валидными параметрами"""
        try:
            cmd = [
                str(self.config.get_vlc_path()),
                "--repeat",
                "--playlist-autostart",
                "--no-qt-error-dialogs",
                "--intf", "dummy",
                "--no-metadata-network-access",
                playlist_uri
            ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )
            logger.success("VLC успешно запущен")
            return True
        except Exception as e:
            logger.critical(f"VLC error: {str(e)}")
            return False

    def stop(self) -> None:
        if self.process:
            self.process.terminate()
            logger.info("VLC остановлен")