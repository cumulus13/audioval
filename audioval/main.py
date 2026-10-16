"""
Core programmatic API for AudioVal.
Handles file validation and tag checking independently of the CLI.
"""
from pathlib import Path
from typing import Tuple
import mutagen
from mutagen import MutagenError

class AudioStatus:
    OK = "OK"
    CORRUPTED = "CORRUPTED"
    EMPTY_TAGS = "EMPTY_TAGS"
    UNSUPPORTED = "UNSUPPORTED"
    ERROR = "ERROR"

def check_audio_file(file_path: Path) -> Tuple[Path, str, str]:
    """
    Checks an audio file for integrity and presence of metadata tags.
    Returns a tuple of (file_path, status, detail_message).
    """
    try:
        audio = mutagen.File(file_path)
        
        if audio is None:
            return file_path, AudioStatus.UNSUPPORTED, "Unsupported or non-audio file format"
            
        tags = audio.tags
        if tags is None or len(tags) == 0:
            return file_path, AudioStatus.EMPTY_TAGS, "No metadata tags found at all"
            
        is_empty = True
        for key, val in tags.items():
            if isinstance(val, list):
                if any(str(v).strip() for v in val):
                    is_empty = False
                    break
            else:
                if str(val).strip():
                    is_empty = False
                    break
                    
        if is_empty:
            return file_path, AudioStatus.EMPTY_TAGS, "Tags exist but only contain empty values"
            
        return file_path, AudioStatus.OK, "File is healthy and tagged"
        
    except MutagenError as e:
        return file_path, AudioStatus.CORRUPTED, f"Corrupted Header/Sync Error: {str(e)}"
    except Exception as e:
        return file_path, AudioStatus.ERROR, f"Unexpected Error: {str(e)}"