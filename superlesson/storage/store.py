import json as json_lib
import logging
import re
from enum import Enum, unique
from pathlib import Path
from typing import Any, Optional

from .utils import format_transcription

logger = logging.getLogger("superlesson")


@unique
class Format(Enum):
    json = "json"
    txt = "txt"


class Store:
    def __init__(self, lesson_root: Path):
        self._lesson_root = lesson_root
        self._storage_root = lesson_root / ".data"

    def _get_storage_path(self, filename: str, format: Format) -> Path:
        if format is Format.json:
            if not self._storage_root.exists():
                self._storage_root.mkdir()
            return self._storage_root / f"{filename}.json"
        return self._lesson_root / f"{filename}.txt"

    @staticmethod
    def _parse_txt(txt_path: Path) -> dict[str, Any]:
            split_texts = re.split(r"====== SLIDE (\S*) \((.*)\) ======", txt_path.read_text())[1:]

            transcriptions = split_texts[2::3]

            timeframes = [
             {"start": start, "end": end}
	                for start, end in map(lambda t: t.split(" - "), split_texts[1::3])
                    ]

            slide_numbers = split_texts[::3]
            def parse_to_int(value):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return None

            transcription_dicts = []

            for i in range(len(transcriptions)):
                transcription_dict = {
                    'transcription': format_transcription(transcriptions[i]),
                    'timeframe': timeframes[i],
                    'number': parse_to_int(slide_numbers[i])
                }
                transcription_dicts.append(transcription_dict)

            return transcription_dicts

    @staticmethod
    def _parse_json(json_path: Path) -> list[dict[str, Any]]:
        json_data = json_path.read_text()
        data = json_lib.loads(json_data)

        for e in data:
            for k, v in e.items():
                if v == "None":
                    e[k] = None

        return data

    @classmethod
    def load(cls, filename: str, load_txt: bool) -> Optional[list[Any]]:
        if load_txt:
            txt_path = cls._get_storage_path(filename, Format.txt)
            if txt_path.exists():
                logger.info(f"Loading {txt_path}")
                return cls._parse_txt(txt_path)

            else:
                logger.info(
                    f"Couldn't load from file {txt_path}, make sure it's properly formatted"
                )

        json_path = cls._get_storage_path(filename, Format.json)
        if json_path.exists():
            logger.info(f"Loading {json_path}")
            return cls._parse_json(json_path)

        return None

    @staticmethod
    def temp_save(txt_data: Any) -> Path:
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            logger.debug(f"Saving temp file to {temp_file.name}")
            temp_file.write(txt_data)

        return temp_path

    def save_json(self, filename: str, data: Any):
        path = self._get_storage_path(filename, Format.json)
        logger.info(f"Saving {path}")
        with open(str(path), "w") as f:
            json_lib.dump(data, f)

    def save_txt(self, filename: str, data: Any):
        path = self._get_storage_path(filename, Format.txt)
        logger.info(f"Saving {path}")
        with open(str(path), "w") as f:
            f.write(data)
