"""
Test script to verify file handling for audio uploads.

This script helps debug issues with file uploads and transcription.
"""

import tempfile
import os
from utils import transcribe_audio

def test_file_handling(audio_file_path):
    """
    Test that file handling works correctly.
    
    Args:
        audio_file_path: Path to a test MP3 file
    """
    print("=" * 60)
    print("File Handling Test")
    print("=" * 60)
    print()
    
    # Check original file
    print(f"1. Original file: {audio_file_path}")
    if not os.path.exists(audio_file_path):
        print("   ✗ File does not exist!")
        return
    
    file_size = os.path.getsize(audio_file_path)
    print(f"   ✓ File exists")
    print(f"   ✓ Size: {file_size / 1024:.2f} KB")
    print()
    
    # Test reading file
    print("2. Reading file...")
    try:
        with open(audio_file_path, 'rb') as f:
            data = f.read()
            print(f"   ✓ Read {len(data)} bytes")
    except Exception as e:
        print(f"   ✗ Error reading file: {e}")
        return
    print()
    
    # Test creating temp file
    print("3. Creating temporary file...")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", mode='wb') as tmp_file:
            tmp_file.write(data)
            tmp_file_path = tmp_file.name
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        
        print(f"   ✓ Created: {tmp_file_path}")
        
        # Verify temp file
        if os.path.exists(tmp_file_path):
            tmp_size = os.path.getsize(tmp_file_path)
            print(f"   ✓ Temp file exists")
            print(f"   ✓ Temp size: {tmp_size / 1024:.2f} KB")
            
            if tmp_size == file_size:
                print(f"   ✓ Sizes match!")
            else:
                print(f"   ✗ Size mismatch! Original: {file_size}, Temp: {tmp_size}")
        else:
            print(f"   ✗ Temp file not found!")
            return
        
    except Exception as e:
        print(f"   ✗ Error creating temp file: {e}")
        return
    print()
    
    # Test transcription (if API key is available)
    print("4. Testing transcription...")
    print("   This will use your AssemblyAI API credits.")
    
    proceed = input("   Proceed with transcription test? (y/n): ")
    if proceed.lower() != 'y':
        print("   Skipped")
        # Clean up
        os.unlink(tmp_file_path)
        return
    
    try:
        print("   Transcribing... (this may take a few minutes)")
        result = transcribe_audio(tmp_file_path)
        
        print(f"   ✓ Transcription successful!")
        print(f"   ✓ Utterances: {len(result.get('utterances', []))}")
        print(f"   ✓ Speakers: {len(set(u['speaker'] for u in result.get('utterances', [])))}")
        print()
        print("   First few utterances:")
        for i, utterance in enumerate(result.get('utterances', [])[:3], 1):
            speaker = utterance.get('speaker', '?')
            text = utterance.get('text', '')[:80]
            print(f"     {i}. Speaker {speaker}: {text}...")
        
    except Exception as e:
        print(f"   ✗ Transcription failed: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
            print()
            print("   ✓ Cleaned up temp file")
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_file_handling.py <path_to_mp3_file>")
        print()
        print("Example:")
        print("  python test_file_handling.py /path/to/audio.mp3")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    test_file_handling(audio_path)



