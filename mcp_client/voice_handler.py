"""
Voice-to-Text Handler for Cursor

Captures audio and converts to text for writing in Cursor editor.
"""
import sys
import json
from typing import Dict, Any, Optional
import subprocess
import tempfile
import os
from pathlib import Path


class VoiceHandler:
    """
    Handles voice input and converts to text.
    Uses multiple fallback methods for speech recognition.
    """
    
    def __init__(self):
        """Initialize voice handler"""
        self.available_methods = self._check_available_methods()
    
    def _check_available_methods(self) -> list:
        """Check which speech recognition methods are available"""
        methods = []
        
        # Check for OpenAI Whisper (via API or local)
        try:
            import openai
            if os.getenv("OPENAI_API_KEY"):
                methods.append("openai_whisper")
        except:
            pass
        
        # Check for SpeechRecognition library
        try:
            import speech_recognition as sr
            methods.append("speech_recognition")
        except:
            pass
        
        # Check for whisper-ctranslate2 (local Whisper)
        try:
            import whisper
            methods.append("whisper_local")
        except:
            pass
        
        return methods
    
    def capture_and_transcribe(
        self,
        duration: int = 5,
        language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Capture audio from microphone and transcribe to text.
        
        Args:
            duration: Recording duration in seconds (default: 5)
            language: Language code (default: pt-BR for Portuguese)
            
        Returns:
            Dict with success status and transcribed text
        """
        if not self.available_methods:
            return {
                "success": False,
                "error": "No speech recognition methods available. Install: pip install SpeechRecognition pyaudio"
            }
        
        try:
            # Try OpenAI Whisper first (best quality)
            if "openai_whisper" in self.available_methods:
                return self._transcribe_openai_whisper(duration, language)
            
            # Try SpeechRecognition library
            elif "speech_recognition" in self.available_methods:
                return self._transcribe_speech_recognition(duration, language)
            
            # Try local Whisper
            elif "whisper_local" in self.available_methods:
                return self._transcribe_whisper_local(duration, language)
            
            else:
                return {
                    "success": False,
                    "error": "No available transcription methods"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription failed: {str(e)}"
            }
    
    def _transcribe_openai_whisper(self, duration: int, language: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            import openai
            import pyaudio
            import wave
            
            # Record audio
            audio_file = self._record_audio(duration)
            if not audio_file:
                return {"success": False, "error": "Failed to record audio"}
            
            # Transcribe with OpenAI
            with open(audio_file, "rb") as f:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=f,
                    language=language.split("-")[0] if "-" in language else language
                )
            
            # Cleanup
            os.unlink(audio_file)
            
            return {
                "success": True,
                "text": transcript["text"].strip(),
                "method": "openai_whisper"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI Whisper failed: {str(e)}"
            }
    
    def _transcribe_speech_recognition(self, duration: int, language: str) -> Dict[str, Any]:
        """Transcribe using SpeechRecognition library"""
        try:
            import speech_recognition as sr
            
            r = sr.Recognizer()
            
            with sr.Microphone() as source:
                print(f"🎤 Gravando por {duration} segundos... (fale agora)")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Try Google Speech Recognition (free, requires internet)
            try:
                text = r.recognize_google(audio, language=language)
                return {
                    "success": True,
                    "text": text,
                    "method": "google_speech"
                }
            except sr.UnknownValueError:
                return {
                    "success": False,
                    "error": "Não foi possível entender o áudio"
                }
            except sr.RequestError as e:
                return {
                    "success": False,
                    "error": f"Erro na API de reconhecimento: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Speech recognition failed: {str(e)}"
            }
    
    def _transcribe_whisper_local(self, duration: int, language: str) -> Dict[str, Any]:
        """Transcribe using local Whisper"""
        try:
            import whisper
            import pyaudio
            import wave
            
            # Record audio
            audio_file = self._record_audio(duration)
            if not audio_file:
                return {"success": False, "error": "Failed to record audio"}
            
            # Load Whisper model
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(audio_file, language=language.split("-")[0])
            
            # Cleanup
            os.unlink(audio_file)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "method": "whisper_local"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Local Whisper failed: {str(e)}"
            }
    
    def _record_audio(self, duration: int) -> Optional[str]:
        """Record audio from microphone"""
        try:
            import pyaudio
            import wave
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print(f"🎤 Gravando {duration} segundos...")
            frames = []
            
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()
            
            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None


def handle_dictate_text(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle dictate_text MCP tool call.
    
    Args:
        args: Tool arguments with optional:
            - duration: Recording duration (default: 5)
            - language: Language code (default: pt-BR)
            - insert_mode: How to insert text (default: "append")
    
    Returns:
        Dict with text to insert and instructions
    """
    handler = VoiceHandler()
    
    duration = args.get("duration", 5)
    language = args.get("language", "pt-BR")
    
    # Capture and transcribe
    result = handler.capture_and_transcribe(duration=duration, language=language)
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "Transcription failed"),
            "text": ""
        }
    
    transcribed_text = result.get("text", "")
    
    return {
        "success": True,
        "text": transcribed_text,
        "method": result.get("method", "unknown"),
        "instructions": f"Insert the following text at cursor position:\n\n{transcribed_text}",
        "insert_mode": args.get("insert_mode", "append")
    }

