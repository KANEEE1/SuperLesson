import logging
import mimetypes
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from .utils import find_lesson_root

logger = logging.getLogger("superlesson")


class FileType(Enum):
    video = "video"
    audio = "audio"
    slides = "slides"


@dataclass
class LessonFile:
    """Class to represent a lesson file."""

    name: str
    path: Path
    file_type: FileType

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.file_type = self._file_type(name)

    @property
    def full_path(self) -> Path:
        return self.path / self.name

    @staticmethod
    def _file_type(name: str) -> FileType:
        """Return the file type of a given file name."""
        mime_type, _ = mimetypes.guess_type(name)
        if mime_type is None:
            raise ValueError(f"File type not found for {name}")
        mime_type = mime_type.split("/")[0]
        match mime_type:
            case "video":
                file_type = FileType.video
            case "audio":
                file_type = FileType.audio
            case "text":
                file_type = FileType.slides
            case _:
                # application
                if name.endswith(".pdf"):
                    file_type = FileType.slides
                else:
                    raise ValueError(f"File type not found for {name}")
        return file_type


class LessonFiles:
    """Class to find all files for a given lesson id."""

    lesson_root: Path

    def __init__(
        self,
        lesson: str,
        transcription_source_path: Optional[Path] = None,
        presentation_path: Optional[Path] = None,
    ):
        self.lesson_root = find_lesson_root(lesson)

        self._files: list[LessonFile] = []

        self._transcription_source = None
        if transcription_source_path is not None:
            # TODO: we should use lesson_root for storing data unconditionally
            root = transcription_source_path.resolve().parent
            if root != self.lesson_root:
                raise ValueError("Transcription source must be in lesson root")
            self._transcription_source = LessonFile(
                transcription_source_path.name,
                root,
            )
        self._presentation = None
        if presentation_path is not None:
            root = presentation_path.resolve().parent
            if root != self.lesson_root:
                raise ValueError("Presentation must be in lesson root")
            self._presentation = LessonFile(
                presentation_path.name, presentation_path.resolve().parent
            )

    @property
    def files(self) -> list[LessonFile]:
        """All usable files in lesson folder."""
        if len(self._files) > 0:
            return self._files

        logger.info("Searching for files...")
        for file in self.lesson_root.iterdir():
            if file.name == "annotations.pdf":
                continue
            if file.is_dir():
                continue
            if file.name.startswith("."):
                continue
            if file.suffix == ".txt":
                continue
            try:
                self._files.append(LessonFile(file.name, self.lesson_root))
                logger.debug(f"Found file: {file}")
            except ValueError:
                logger.debug(f"Skipping file: {file}")

        # TODO: test for duplicate file types

        return self._files

    @property
    def transcription_source(self) -> LessonFile:
        """The file to be used for transcription."""
        if self._transcription_source is None:
            files = self._find_lesson_files([FileType.video, FileType.audio])
            if not files:
                raise ValueError(f"Transcription file not found on {self.lesson_root}")
            self._transcription_source = files[0]
            logger.debug(f"Transcription source: {self._transcription_source}")

        return self._transcription_source

    @property
    def presentation(self) -> LessonFile:
        """The file to be used for annotation."""
        if self._presentation is None:
            files = self._find_lesson_files([FileType.slides])
            for file in files:
                if file.name.endswith(".pdf"):
                    self._presentation = file
                    logger.debug(f"Presentation: {self._presentation}")
                    break
            if self._presentation is None:
                raise ValueError(f"Presentation file not found on {self.lesson_root}")

        return self._presentation

    def _find_lesson_files(
        self, accepted_types: list[Optional[FileType]]
    ) -> list[LessonFile]:
        for file_type in accepted_types:
            if file_type is None:
                continue
            files = self._get_files(file_type)
            if len(files) > 0:
                return files

        return []

    def _get_files(self, file_type: FileType) -> list[LessonFile]:
        """Get all files of a given type."""
        return [file for file in self.files if file.file_type == file_type]
