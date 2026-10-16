import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from mutagen import MutagenError

from audioval.main import check_audio_file, AudioStatus

@pytest.fixture
def mock_path():
    return Path("fake_audio_file.mp3")

@patch("audioval.main.mutagen.File")
def test_unsupported_file(mock_mutagen_file, mock_path):
    mock_mutagen_file.return_value = None
    path, status, detail = check_audio_file(mock_path)
    
    assert path == mock_path
    assert status == AudioStatus.UNSUPPORTED
    assert "Unsupported" in detail

@patch("audioval.main.mutagen.File")
def test_no_tags_at_all(mock_mutagen_file, mock_path):
    mock_audio = MagicMock()
    mock_audio.tags = None
    mock_mutagen_file.return_value = mock_audio
    
    path, status, detail = check_audio_file(mock_path)
    assert status == AudioStatus.EMPTY_TAGS

@patch("audioval.main.mutagen.File")
def test_empty_string_tags(mock_mutagen_file, mock_path):
    mock_audio = MagicMock()
    mock_audio.tags = {
        "title": [""],
        "artist": ["   "],
        "album": ""
    }
    mock_mutagen_file.return_value = mock_audio
    
    path, status, detail = check_audio_file(mock_path)
    assert status == AudioStatus.EMPTY_TAGS

@patch("audioval.main.mutagen.File")
def test_healthy_tagged_file(mock_mutagen_file, mock_path):
    mock_audio = MagicMock()
    mock_audio.tags = {
        "title": ["Bohemian Rhapsody"],
        "artist": ["Queen"]
    }
    mock_mutagen_file.return_value = mock_audio
    
    path, status, detail = check_audio_file(mock_path)
    assert status == AudioStatus.OK

@patch("audioval.main.mutagen.File")
def test_corrupted_file(mock_mutagen_file, mock_path):
    mock_mutagen_file.side_effect = MutagenError("Lost sync")
    path, status, detail = check_audio_file(mock_path)
    
    assert status == AudioStatus.CORRUPTED

@patch("audioval.main.mutagen.File")
def test_unexpected_error(mock_mutagen_file, mock_path):
    mock_mutagen_file.side_effect = PermissionError("Access denied")
    path, status, detail = check_audio_file(mock_path)
    
    assert status == AudioStatus.ERROR