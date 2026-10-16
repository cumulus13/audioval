"""
Command-line interface and terminal UI for AudioVal.
"""
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn
)
from rich.theme import Theme

# Import core logic from main.py
from audioval.main import check_audio_file, AudioStatus

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
})

console = Console(theme=custom_theme)

def run_cli():
    parser = argparse.ArgumentParser(
        description="🎵 Advanced Audio Validator: Detect corrupted files and empty tags."
    )
    parser.add_argument("-d", "--dir", type=str, required=True, help="Target directory to scan")
    parser.add_argument(
        "-e", "--ext", nargs="+", 
        default=[".mp3", ".flac", ".m4a", ".ogg", ".wav", ".wma"],
        help="Extensions to scan (default: .mp3 .flac .m4a .ogg .wav .wma)"
    )
    parser.add_argument("-w", "--workers", type=int, default=4, help="Concurrent workers (default: 4)")
    
    # NEW MODES
    parser.add_argument("-v", "--verbose", action="store_true", help="Show details for all files, including healthy ones")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (logs background operations & tracebacks)")
    
    args = parser.parse_args()

    # Configure Rich Logging
    if args.debug:
        logging.basicConfig(
            level="DEBUG",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)]
        )
    else:
        # Suppress standard logging output if debug is not enabled
        logging.basicConfig(
            level="WARNING",
            format="%(message)s",
            handlers=[logging.NullHandler()]
        )
        
    log = logging.getLogger("audioval")
    
    scan_dir = Path(args.dir)
    if not scan_dir.is_dir():
        console.print(f"[error]❌ Error: Directory '{scan_dir}' does not exist.[/error]")
        sys.exit(1)
        
    extensions = set(ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args.ext)
    
    console.print(f"[info]🔍 Scanning '{scan_dir}' for audio files...[/info]")
    
    # Debug Logs
    log.debug(f"Target extensions: {extensions}")
    log.debug(f"Allocated workers: {args.workers}")
    
    files_to_scan = [p for p in scan_dir.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
    
    if not files_to_scan:
        console.print(f"[warning]⚠️ No audio files found matching extensions: {', '.join(extensions)}[/warning]")
        sys.exit(0)
        
    console.print(f"📦 Found {len(files_to_scan)} files. Starting analysis with {args.workers} workers...\n")
    
    results: List[Tuple[Path, str, str]] = []
    
    # We disable the progress bar in debug mode so it doesn't clash with log streaming
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        disable=args.debug 
    ) as progress:
        task = progress.add_task("[cyan]Analyzing audio tracks...", total=len(files_to_scan))
        
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_file = {}
            for f in files_to_scan:
                log.debug(f"Submitting to worker pool: {f.name}")
                future_to_file[executor.submit(check_audio_file, f)] = f
                
            for future in as_completed(future_to_file):
                f = future_to_file[future]
                try:
                    res = future.result()
                    results.append(res)
                    log.debug(f"Result for {f.name}: {res[1]}")
                except Exception as e:
                    # Logs rich traceback if an unhandled exception violently crashes a worker
                    log.exception(f"Fatal error analyzing {f.name}")
                    results.append((f, AudioStatus.ERROR, str(e)))
                
                if not args.debug:
                    progress.advance(task)
                
    ok_files = []
    corrupted_files = []
    empty_tag_files = []
    unsupported_files = []
    
    for res in results:
        status = res[1]
        if status == AudioStatus.OK:
            ok_files.append(res)
        elif status in (AudioStatus.CORRUPTED, AudioStatus.ERROR):
            corrupted_files.append(res)
        elif status == AudioStatus.EMPTY_TAGS:
            empty_tag_files.append(res)
        elif status == AudioStatus.UNSUPPORTED:
            unsupported_files.append(res)

    # ==========================================
    # VERBOSE MODE: Print healthy files table
    # ==========================================
    if args.verbose and ok_files:
        console.print()
        success_table = Table(title="✅ Healthy Audio Files", show_header=True, header_style="bold green")
        success_table.add_column("Status", style="dim", width=17)
        success_table.add_column("File Path", overflow="fold")
        success_table.add_column("Details")
        
        for path, status, detail in ok_files:
            rel_path = path.relative_to(scan_dir) if scan_dir in path.parents else path
            success_table.add_row("✅ [success]OK[/success]", str(rel_path), detail)
            
        console.print(success_table)
            
    # Problematic Files Table
    problem_table = Table(title="⚠️ Problematic Audio Files", show_header=True, header_style="bold magenta")
    problem_table.add_column("Status", style="dim", width=17)
    problem_table.add_column("File Path", overflow="fold")
    problem_table.add_column("Details")
    
    for path, status, detail in corrupted_files:
        rel_path = path.relative_to(scan_dir) if scan_dir in path.parents else path
        problem_table.add_row("💥 [error]CORRUPTED[/error]", str(rel_path), detail)
        
    for path, status, detail in empty_tag_files:
        rel_path = path.relative_to(scan_dir) if scan_dir in path.parents else path
        problem_table.add_row("🏷️ [warning]EMPTY TAGS[/warning]", str(rel_path), detail)
        
    if corrupted_files or empty_tag_files:
        console.print()
        console.print(problem_table)
        console.print()
        
    summary_table = Table(title="📊 Scan Summary", show_header=True)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right")
    
    summary_table.add_row("Total Files Scanned", str(len(files_to_scan)))
    summary_table.add_row("✅ Healthy & Tagged", f"[success]{len(ok_files)}[/success]")
    summary_table.add_row("🏷️ Missing Tags", f"[warning]{len(empty_tag_files)}[/warning]")
    summary_table.add_row("💥 Corrupted / Errors", f"[error]{len(corrupted_files)}[/error]")
    summary_table.add_row("🤷 Unsupported Format", str(len(unsupported_files)))
    
    console.print("\n")
    console.print(summary_table)

    if corrupted_files or empty_tag_files:
        sys.exit(1)
    else:
        console.print("\n🎉 [success]All files are healthy and perfectly tagged![/success]")
        sys.exit(0)

def main():
    try:
        run_cli()
    except KeyboardInterrupt:
        console.print("\n[warning]Scan interrupted by user. Exiting...[/warning]")
        sys.exit(130)

if __name__ == "__main__":
    main()