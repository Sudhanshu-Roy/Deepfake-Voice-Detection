import librosa
import numpy as np

from src.config import (
    SR,
    CHUNK_DURATION,
    N_MELS
)

def load_audio(file_path):
    audio, sr = librosa.load(
        file_path,
        sr=SR
    )

    return audio

def split_audio(audio):
    
    chunk_size = SR * CHUNK_DURATION

    chunks = []

    for i in range(
        0,
        len(audio),
        chunk_size
    ):
        
        chunk = audio[i:i+chunk_size]

        if len(chunk) == chunk_size:
            chunks.append(chunk)

    return chunks

def create_mel(chunk):

    mel = librosa.feature.melspectrogram(
        y=chunk,
        sr=SR,
        n_mels=N_MELS
    )

    mel_db = librosa.power_to_db(
        mel,
        ref=np.max
    )

    return mel_db

def preprocess_audio(file_path):

    audio = load_audio(file_path)

    chunks = split_audio(audio)

    processed = []

    for chunk in chunks:

        mel = create_mel(chunk)

        processed.append(mel)

    processed = np.array(
        processed,
        dtype=np.float32
    )

    processed = (
        processed + 80
    ) / 80

    processed = processed[
        ...,
        np.newaxis
    ]

    return processed