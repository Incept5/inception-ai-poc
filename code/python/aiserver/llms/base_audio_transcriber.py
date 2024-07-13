from abc import ABC, abstractmethod
from typing import BinaryIO, Iterator, Union

class BaseAudioTranscriber(ABC):
    """
    Base class for audio transcription services.
    """

    @abstractmethod
    def transcribe_audio(self, audio_stream: BinaryIO, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Transcribe an audio stream to text.

        Args:
            audio_stream (BinaryIO): A binary stream of audio data.
            stream (bool): If True, return an iterator of transcribed segments. If False, return the full transcription.

        Returns:
            Union[str, Iterator[str]]: Either the full transcription as a string (if stream=False) or
                                       an iterator that yields transcribed text segments (if stream=True).

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("The transcribe_audio method must be implemented by subclasses.")