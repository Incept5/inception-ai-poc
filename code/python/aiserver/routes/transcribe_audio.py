from flask import Blueprint, request, Response, stream_with_context
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print

transcribe_audio_bp = Blueprint('transcribe_audio', __name__)

@transcribe_audio_bp.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    audio_file = request.files.get('audio')
    
    if not audio_file:
        return "No audio file provided", 400

    transcriber = LLMManager.get_audio_transcriber()
    
    if not transcriber:
        return "Audio transcription is not available", 503

    def generate():
        try:
            for chunk in transcriber.transcribe_audio_stream(audio_file):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            debug_print(f"Error during audio transcription: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')