from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml
from mutagen import File as MutagenFile


@dataclass(frozen=True)
class TrackInfo:
    path: str
    ext: str
    size_bytes: int
    artist: Optional[str]
    album: Optional[str]
    title: Optional[str]
    tracknumber: Optional[str]
    discnumber: Optional[str]


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise ValueError(f"Config must contain a YAML mapping (dict). Got: {type(cfg).__name__}")

    return cfg


def iter_audio_files(root: Path, exts: set[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def _get_first_tag(audio, keys: list[str]) -> Optional[str]:
    if not audio or not getattr(audio, "tags", None):
        return None
    for k in keys:
        v = audio.tags.get(k)
        if v is None:
            continue
        if isinstance(v, (list, tuple)) and v:
            s = str(v[0]).strip()
            return s or None
        s = str(v).strip()
        return s or None
    return None


def read_track_info(path: Path) -> TrackInfo:
    audio = MutagenFile(path)
    return TrackInfo(
        path=str(path),
        ext=path.suffix.lower(),
        size_bytes=path.stat().st_size,
        artist=_get_first_tag(audio, ["TPE1", "artist", "ARTIST"]),
        album=_get_first_tag(audio, ["TALB", "album", "ALBUM"]),
        title=_get_first_tag(audio, ["TIT2", "title", "TITLE"]),
        tracknumber=_get_first_tag(audio, ["TRCK", "tracknumber", "TRACKNUMBER"]),
        discnumber=_get_first_tag(audio, ["TPOS", "discnumber", "DISCNUMBER"]),
    )


def scan_library(root: Path, exts: set[str]) -> list[TrackInfo]:
    tracks: list[TrackInfo] = []
    for f in iter_audio_files(root, exts):
        try:
            tracks.append(read_track_info(f))
        except Exception:
            # Continue scanning even if one file has corrupt tags or an unreadable header.
            tracks.append(
                TrackInfo(
                    path=str(f),
                    ext=f.suffix.lower(),
                    size_bytes=f.stat().st_size,
                    artist=None,
                    album=None,
                    title=None,
                    tracknumber=None,
                    discnumber=None,
                )
            )
    return tracks


def summarize(tracks: list[TrackInfo]) -> str:
    total = len(tracks)
    total_bytes = sum(t.size_bytes for t in tracks)

    def missing(field: str) -> int:
        return sum(1 for t in tracks if getattr(t, field) in (None, ""))

    lines = []
    lines.append(f"Files scanned: {total}")
    lines.append(f"Total size: {total_bytes/1024/1024:.1f} MiB")
    lines.append("Missing tags:")
    for field in ["artist", "album", "title", "tracknumber"]:
        lines.append(f"  {field}: {missing(field)}")
    return "\n".join(lines)


def main() -> int:
    cfg = load_config(Path("config.yaml"))
    source_root = Path(cfg["source_root"])
    exts = {e.lower() for e in cfg.get("audio_extensions", [])}

    if not source_root.exists():
        print(f"ERROR: source_root does not exist: {source_root}")
        return 2

    tracks = scan_library(source_root, exts)
    print(summarize(tracks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
