"""
Created on Tue Aug 11 21:02:52 2021

@author: Rick Ross
@description: Simple audio steganography using LSB example.
"""

# This script is an extension of Sumit Arora's Audio Steganography example:
# https://sumit-arora.medium.com/audio-steganography-the-art-of-hiding-secrets-within-earshot-part-2-of-2-c76b1be719b3

# We will use wave package available in native Python installation to read and 
# write .wav audio file
import wave
from pathlib import Path

def new_audio_path(image_path: Path) -> Path:
    new_name = image_path.stem + '_stego' + image_path.suffix
    new_path = Path(image_path.parent / new_name)
    return new_path

def encode_audio(message: str, audio_path: Path) -> Path:
        
    # read wave audio file
    song = wave.open(str(audio_path), mode='rb')
    
    # Read frames and convert to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    # Append dummy data to fill out rest of the bytes. Receiver shall detect 
    # and remove these characters.
    message = message + int((len(frame_bytes)-(len(message)*8*8))/8) *'#'
    
    # Convert text to bit array
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in message])))
    
    # Replace LSB of each byte of the audio data by one bit from the text bit array
    for i, bit in enumerate(bits):
       frame_bytes[i] = (frame_bytes[i] & ~1) | bit
        
    # Get the modified bytes
    frame_modified = bytes(frame_bytes)
    
    new_path = new_audio_path(audio_path)
    
    # Write bytes to a new wave audio file
    with wave.open(str(new_path), 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
        
    song.close()
    
    return new_path
    
def decode_audio(audio_path: Path) -> str:
    
    song = wave.open(str(audio_path), mode='rb')
    
    # Convert audio to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    # Extract the LSB of each byte
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    # Convert byte array back to string
    string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
    # Cut off at the filler characters
    decoded = string.split("###")[0]
    
    # Print the extracted text
    song.close()
    
    return decoded

encoded_path = encode_audio("BUY GME NOW", Path("Deck_The_Halls_Short2.wav"))
print(decode_audio(encoded_path))