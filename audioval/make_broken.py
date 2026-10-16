# make_broken.py
import os

print("Creating mathematically broken audio files for testing...")

# 1. Create a corrupted MP3
# It starts with a valid "ID3" magic header so Mutagen thinks it's an MP3,
# but the frame data immediately following it is total garbage.
with open("broken_fake.mp3", "wb") as f:
    f.write(b"ID3\x03\x00\x00\x00\x00\x00\x7F" + b"THIS IS GARBAGE BINARY DATA" * 100)

# 2. Create a corrupted FLAC
# It starts with the valid "fLaC" magic header, but the mandatory 
# STREAMINFO metadata block is deliberately mangled.
with open("broken_fake.flac", "wb") as f:
    f.write(b"fLaC\x80\x00\x00\x22" + b"GARBAGE FLAC BLOCKS" * 100)

print("Done. Now run: audioval -d .")