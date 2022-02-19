import hashlib
import logging
from copy import deepcopy
from pathlib import Path
from typing import Tuple
from urllib.request import urlopen, Request
from urllib.parse import quote

from pelican import signals
from kagamitypes import KagamiBadgeDefinition


logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"


def shields_io_escape(s: str) -> str:
    return s.replace("-", "--").replace("_", "__").replace(" ", "_")


def get_svg_filename(label: str, message: str, color: str) -> str:
    buffer = (label + message + color).encode()
    return f"{hashlib.sha1(buffer).hexdigest()}.svg"


def get_shields_io_svg(label: str, message: str, color: str) -> bytes:
    label = shields_io_escape(label)
    message = shields_io_escape(message)
    color = shields_io_escape(color)
    param = quote(f"{label}-{message}-{color}")
    url = f"https://img.shields.io/badge/{param}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    logger.info("Downloading badge {label}-{message}-{color} at {url}".format(
        url=url, label=label, message=message, color=color))
    response = urlopen(request)
    return response.read()


def save_badges(sender):
    badges: Tuple[KagamiBadgeDefinition] = sender.settings['KAGAMI_BADGES']
    sender.settings['KAGAMI_CACHED_BADGES'] = []
    badge_dir = Path(sender.path).parent / \
        sender.output_path / "images" / "badges"
    badge_dir.mkdir(parents=True, exist_ok=True)
    for badge in badges:
        cached_badge = deepcopy(badge)
        if "link" in badge:
            badge.pop("link")
        filename = get_svg_filename(**badge)
        cached_badge['filename'] = filename
        sender.settings['KAGAMI_CACHED_BADGES'].append(cached_badge)
        badge_file = badge_dir / filename
        if badge_file.exists():
            logger.info(
                "Badge {label}-{message}-{color} found at {path}".format(path=badge_file, **badge))
        else:
            data = get_shields_io_svg(**badge)
            Path(badge_dir / filename).write_bytes(data)
            logger.info(
                "Badge {label}-{message}-{color} saved as {path}".format(path=badge_file, **badge))


def register():
    signals.initialized.connect(save_badges)
