import pytest
import sys
import logging
from unittest.mock import patch
from pathlib import Path

# Import the CLI runner function and status codes
from audioval.cli import run_cli
from audioval.main import AudioStatus

def test_cli_missing_args():
    with patch.object(sys, 'argv', ['audioval']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 2

def test_cli_invalid_directory():
    fake_dir = "/this/path/absolutely/does/not/exist/999"
    with patch.object(sys, 'argv', ['audioval', '-d', fake_dir]):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 1

def test_cli_empty_directory(tmp_path):
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

def test_cli_custom_extensions_no_match(tmp_path):
    dummy_file = tmp_path / "document.txt"
    dummy_file.write_text("Hello world")
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '-e', 'flac', 'mp3']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

def test_cli_verbose_flag(tmp_path):
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '-v']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

@patch("audioval.cli.logging.basicConfig")
def test_cli_debug_flag(mock_basic_config, tmp_path):
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '--debug']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

# --- NEW TESTS TO COVER THE FILE PROCESSING LOOP ---

@patch("audioval.cli.check_audio_file")
def test_cli_full_scan_healthy(mock_check, tmp_path):
    """Simulate a scan finding healthy files to cover the success tables."""
    dummy_file = tmp_path / "song.mp3"
    dummy_file.write_text("fake")
    
    mock_check.return_value = (dummy_file, AudioStatus.OK, "Healthy")
    
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '-v']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

@patch("audioval.cli.check_audio_file")
def test_cli_full_scan_problems(mock_check, tmp_path):
    """Simulate a scan finding empty tags and corrupted files to cover the error tables."""
    f1 = tmp_path / "empty.mp3"
    f2 = tmp_path / "corrupt.mp3"
    f1.write_text("fake1")
    f2.write_text("fake2")
    
    def side_effect(filepath):
        if "empty" in filepath.name:
            return (filepath, AudioStatus.EMPTY_TAGS, "Empty tags found")
        return (filepath, AudioStatus.CORRUPTED, "Corrupted frame")
        
    mock_check.side_effect = side_effect
    
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        # Script correctly exits with 1 when problems are found
        assert exc_info.value.code == 1