import subprocess
import time
import socket

from loguru import logger


class VLCController:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.http_port = 8080  # Можно переместить в Config

    def is_port_available(self, port):
        """Проверка доступности порта перед запуском"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('localhost', port))
                return True
        except:
            return False

    def start(self, playlist_uri: str) -> bool:
        """Запуск VLC с валидными параметрами и проверкой порта"""
        try:
            # Проверяем порт перед запуском
            if not self.is_port_available(self.http_port):
                logger.error(f"Порт {self.http_port} занят. Выберите другой порт.")
                return False

            # Используем URI напрямую, без дополнительного форматирования
            # playlist_uri уже должен быть в формате file://...
            cmd = [
                str(self.config.get_vlc_path()),
                "--sout", f"#standard{{access=http,mux=ts,dst=:{self.http_port}}}",
                "--sout-keep",
                "--loop",
                "--playlist-autostart",
                "--no-qt-error-dialogs",
                "--intf", "dummy",
                "--no-metadata-network-access",
                "--file-logging",
                "--logfile", str(self.config.dirs['logs'] / 'vlc.log'),
                playlist_uri
            ]

            logger.info(f"Запуск VLC на порту {self.http_port}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,  # Перенаправляем вывод для диагностики
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )

            # Небольшая задержка и проверка процесса
            time.sleep(2)
            if self.process.poll() is not None:
                logger.error(f"VLC завершился с кодом {self.process.returncode}")
                return False

            logger.success("VLC успешно запущен")
            return True

        except Exception as e:
            logger.critical(f"VLC error: {str(e)}")
            return False

    def is_running(self) -> bool:
        """Проверка, запущен ли VLC"""
        return self.process is not None and self.process.poll() is None

    def restart(self, playlist_uri: str) -> bool:
        """Перезапуск VLC в случае сбоя"""
        logger.info("Перезапуск VLC...")
        self.stop()
        return self.start(playlist_uri)

    def stop(self) -> None:
        if self.process:
            try:
                self.process.terminate()
                # Ждем корректного завершения
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Если не завершается по-хорошему, убиваем
                self.process.kill()
            logger.info("VLC остановлен")
