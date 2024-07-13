import os
from typing import BinaryIO, Iterator, Union
import openai
from llms.base_audio_transcriber import BaseAudioTranscriber

class OpenAIAudioTranscriber(BaseAudioTranscriber):
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        openai.api_key = api_key

    def transcribe_audio(self, audio_stream: BinaryIO, stream: bool = False) -> Union[str, Iterator[str]]:
        if stream:
            return self._stream_transcribe(audio_stream)
        else:
            return self._full_transcribe(audio_stream)

    def _full_transcribe(self, audio_stream: BinaryIO) -> str:
        response = openai.Audio.transcribe("whisper-1", audio_stream)
        return response["text"]

    def _stream_transcribe(self, audio_stream: BinaryIO) -> Iterator[str]:
        response = openai.Audio.transcribe("whisper-1", audio_stream, stream=True)
        for chunk in response:
            if chunk.get("text"):
                yield chunk["text"]