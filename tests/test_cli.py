import pytest
import sys
import logging
from unittest.mock import patch
from pathlib import Path

# Import the CLI runner function
from audioval.cli import run_cli

def test_cli_missing_args():
    """Test that argparse correctly catches missing required -d argument."""
    with patch.object(sys, 'argv', ['audioval']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        # Argparse exits with code 2 on syntax/missing arg errors
        assert exc_info.value.code == 2

def test_cli_invalid_directory():
    """Test the custom validation for non-existent directories."""
    fake_dir = "/this/path/absolutely/does/not/exist/999"
    with patch.object(sys, 'argv', ['audioval', '-d', fake_dir]):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        # Our script explicitly exits with 1 for invalid directories
        assert exc_info.value.code == 1

def test_cli_empty_directory(tmp_path):
    """Test scanning a directory with no matching files."""
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        # Script should exit 0 cleanly if no files needed scanning
        assert exc_info.value.code == 0

def test_cli_custom_extensions_no_match(tmp_path):
    """Test that the extension parser works correctly."""
    dummy_file = tmp_path / "document.txt"
    dummy_file.write_text("Hello world")
    
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '-e', 'flac', 'mp3']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

def test_cli_verbose_flag(tmp_path):
    """Test that the -v / --verbose flag parses and executes cleanly."""
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '-v']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0

@patch("audioval.cli.logging.basicConfig")
def test_cli_debug_flag(mock_basic_config, tmp_path):
    """Test that the --debug flag successfully triggers debug logging configuration."""
    with patch.object(sys, 'argv', ['audioval', '-d', str(tmp_path), '--debug']):
        with pytest.raises(SystemExit) as exc_info:
            run_cli()
        assert exc_info.value.code == 0
        
        # Verify that logging.basicConfig was triggered with the DEBUG level
        mock_basic_config.assert_called_once()
        _, kwargs = mock_basic_config.call_args
        assert kwargs.get("level") == "DEBUG"
        assert "handlers" in kwargs