import argparse
import datetime
import hashlib
import json
import shutil
from pathlib import Path

DEFAULT_WEBSITE_DIR = Path(r"C:\Users\Tempestgf\Coding\Web\mobilwheelwebsite")
DEFAULT_BASE_URL = "https://mobilwheel.com/update"


def sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 512), b""):
            digest.update(chunk)
    return digest.hexdigest()


def patch_app_version(file_path: Path, version: str) -> None:
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    output = []
    for line in lines:
        if line.startswith("APP_VERSION = "):
            output.append(f'APP_VERSION = "{version}"')
        else:
            output.append(line)
    file_path.write_text("\n".join(output) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica una nueva actualizacion para Mobile Wheel Server")
    parser.add_argument("--installer", required=True, help="Ruta del .exe instalador")
    parser.add_argument("--version", required=True, help="Version de release, ej: 1.0.1")
    parser.add_argument("--notes", default="Mejoras de estabilidad.", help="Notas de la version")
    parser.add_argument("--force", action="store_true", help="Marcar update obligatorio")
    parser.add_argument("--channel", default="stable", help="Canal de release")
    parser.add_argument("--min-supported-version", default="1.0.0", help="Version minima soportada")
    parser.add_argument("--website-dir", default=str(DEFAULT_WEBSITE_DIR), help="Ruta del proyecto web mobilwheelwebsite")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL publica para descargas")
    parser.add_argument("--set-app-version", action="store_true", help="Actualizar APP_VERSION en app_version.py")
    args = parser.parse_args()

    installer_path = Path(args.installer).resolve()
    if not installer_path.exists():
        raise FileNotFoundError(f"No existe instalador: {installer_path}")

    website_dir = Path(args.website_dir).resolve()
    update_dir = website_dir / "public" / "update"
    update_dir.mkdir(parents=True, exist_ok=True)

    # Copy installer into web public/update with dynamic version name
    dest_exe_name = f"MobileWheelServer-{args.version}-setup.exe"
    dest_installer = update_dir / dest_exe_name
    shutil.copy2(installer_path, dest_installer)

    checksum = sha256_file(dest_installer)
    published_at = (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    download_url = f"{args.base_url.rstrip('/')}/{dest_installer.name}"

    manifest = {
        "app": "mobile-wheel-server",
        "channel": args.channel,
        "version": args.version,
        "min_supported_version": args.min_supported_version,
        "force": args.force,
        "published_at": published_at,
        "notes": args.notes,
        "download_url": download_url,
        "sha256": checksum,
    }

    manifest_path = update_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.set_app_version:
        patch_app_version(Path(__file__).parent.parent / "app_version.py", args.version)

    print("Release publicado localmente")
    print(f"Installer: {dest_installer}")
    print(f"Manifest:  {manifest_path}")
    print(f"Version:   {args.version}")
    print(f"SHA256:    {checksum}")
    print(f"URL:       {download_url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
