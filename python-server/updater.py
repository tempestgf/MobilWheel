import hashlib
import logging
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

from app_version import APP_NAME, APP_VERSION, UPDATE_MANIFEST_URL

logger = logging.getLogger(__name__)


class UpdateError(Exception):
    pass


class AppUpdater:
    def __init__(self, manifest_url: str = UPDATE_MANIFEST_URL, current_version: str = APP_VERSION):
        self.manifest_url = manifest_url
        self.current_version = current_version

    def check_for_updates(self, timeout: int = 10) -> Dict:
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-Agent", f"{APP_NAME}/{self.current_version}")]
            urllib.request.install_opener(opener)
            
            with urllib.request.urlopen(self.manifest_url, timeout=timeout) as response:
                payload = response.read().decode("utf-8")

            import json

            data = json.loads(payload)
            latest_version = str(data.get("version", "")).strip()
            if not latest_version:
                raise UpdateError("Manifest sin campo version")

            update_available = self._is_newer_version(latest_version, self.current_version)
            data["update_available"] = update_available
            data["current_version"] = self.current_version
            return data
        except urllib.error.URLError as exc:
            raise UpdateError(f"No se pudo consultar el servidor de actualizaciones: {exc}") from exc
        except Exception as exc:
            raise UpdateError(f"Error revisando actualizaciones: {exc}") from exc

    def download_update(self, download_url: str, expected_sha256: Optional[str] = None) -> Path:
        if not download_url:
            raise UpdateError("No se recibió URL de descarga")

        updates_dir = Path(tempfile.gettempdir()) / "mobilwheel_updates"
        updates_dir.mkdir(parents=True, exist_ok=True)

        filename = download_url.split("/")[-1] or "mobilewheel_update.bin"
        target_file = updates_dir / filename

        if target_file.exists():
            try:
                target_file.unlink()
            except PermissionError:
                import uuid
                filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                target_file = updates_dir / filename

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-Agent", f"{APP_NAME}/{self.current_version}")]
            urllib.request.install_opener(opener)
            
            with urllib.request.urlopen(download_url, timeout=60) as response, open(target_file, "wb") as output:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    output.write(chunk)

            if expected_sha256:
                actual_hash = self._sha256_file(target_file)
                if actual_hash.lower() != expected_sha256.lower():
                    target_file.unlink(missing_ok=True)
                    raise UpdateError("Checksum SHA256 inválido en el archivo descargado")

            return target_file
        except urllib.error.URLError as exc:
            raise UpdateError(f"No se pudo descargar la actualización: {exc}") from exc
        except Exception as exc:
            raise UpdateError(f"Error descargando actualización: {exc}") from exc

    def launch_installer(self, installer_path: Path, silent: bool = False) -> None:
        if not installer_path.exists():
            raise UpdateError(f"Instalador no encontrado: {installer_path}")

        import sys
        if hasattr(sys, 'frozen'):
            # Estamos corriendo como ejecutable de PyInstaller
            current_exe = Path(sys.executable)
            bat_path = installer_path.with_suffix('.bat')
            
            # Script batch que espera a que cierre el actual, copia el nuevo encima y lo ejecuta
            bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
copy /Y "{installer_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
            bat_path.write_text(bat_content, encoding="utf-8")
            
            try:
                subprocess.Popen([str(bat_path)], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as exc:
                raise UpdateError(f"No se pudo reemplazar el ejecutable: {exc}") from exc
        else:
            args = [str(installer_path)]
            if silent:
                args.append("/S")

            try:
                if os.name == "nt":
                    subprocess.Popen(args, shell=False)
                else:
                    subprocess.Popen(args)
            except Exception as exc:
                raise UpdateError(f"No se pudo iniciar el instalador: {exc}") from exc

    @staticmethod
    def _sha256_file(file_path: Path) -> str:
        digest = hashlib.sha256()
        with open(file_path, "rb") as fp:
            for chunk in iter(lambda: fp.read(1024 * 512), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _parse_version(version: str) -> Tuple[int, ...]:
        parts = []
        for piece in version.split("."):
            try:
                parts.append(int(piece))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    def _is_newer_version(self, latest: str, current: str) -> bool:
        return self._parse_version(latest) > self._parse_version(current)
