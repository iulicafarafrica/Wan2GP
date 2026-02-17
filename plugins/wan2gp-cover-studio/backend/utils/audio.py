import numpy as np
import librosa
from typing import Tuple
import soundfile as sf

class AudioProcessor:
    def __init__(self):
        print("[AudioProcessor] Initialized")
    
    def separate_vocals(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        print(f"[AudioProcessor] Separating vocals from audio of length {len(audio)} samples")
        
        stft = librosa.stft(audio)
        
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        harmonic_mag, percussive_mag = librosa.decompose.hpss(magnitude)
        
        vocals_stft = harmonic_mag * np.exp(1j * phase)
        instrumental_stft = percussive_mag * np.exp(1j * phase)
        
        vocals = librosa.istft(vocals_stft)
        instrumental = librosa.istft(instrumental_stft)
        
        target_length = len(audio)
        if len(vocals) < target_length:
            vocals = np.pad(vocals, (0, target_length - len(vocals)))
        else:
            vocals = vocals[:target_length]
        
        if len(instrumental) < target_length:
            instrumental = np.pad(instrumental, (0, target_length - len(instrumental)))
        else:
            instrumental = instrumental[:target_length]
        
        print(f"[AudioProcessor] Separated vocals: {len(vocals)} samples, instrumental: {len(instrumental)} samples")
        
        return vocals, instrumental
    
    def mix_audio(
        self,
        vocals: np.ndarray,
        instrumental: np.ndarray,
        sr: int,
        vocal_volume: float = 1.0,
        instrumental_volume: float = 0.8
    ) -> np.ndarray:
        print(f"[AudioProcessor] Mixing vocals ({len(vocals)} samples) with instrumental ({len(instrumental)} samples)")
        
        max_length = max(len(vocals), len(instrumental))
        
        if len(vocals) < max_length:
            vocals = np.pad(vocals, (0, max_length - len(vocals)))
        if len(instrumental) < max_length:
            instrumental = np.pad(instrumental, (0, max_length - len(instrumental)))
        
        mixed = vocals * vocal_volume + instrumental * instrumental_volume
        
        max_amplitude = np.abs(mixed).max()
        if max_amplitude > 0.99:
            mixed = mixed / max_amplitude * 0.99
        
        print(f"[AudioProcessor] Mixed audio length: {len(mixed)} samples")
        
        return mixed
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
        print("[AudioProcessor] Normalizing audio")
        
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            target_rms = 10 ** (target_level / 20)
            scaling_factor = target_rms / rms
            audio = audio * scaling_factor
        
        audio = np.clip(audio, -1.0, 1.0)
        
        return audio
    
    def apply_fade(
        self,
        audio: np.ndarray,
        sr: int,
        fade_in_duration: float = 0.1,
        fade_out_duration: float = 0.1
    ) -> np.ndarray:
        print(f"[AudioProcessor] Applying fade in ({fade_in_duration}s) and fade out ({fade_out_duration}s)")
        
        fade_in_samples = int(fade_in_duration * sr)
        fade_out_samples = int(fade_out_duration * sr)
        
        audio = audio.copy()
        
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        audio[:fade_in_samples] *= fade_in_curve
        
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        audio[-fade_out_samples:] *= fade_out_curve
        
        return audio
    
    def resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        if orig_sr == target_sr:
            return audio
        
        print(f"[AudioProcessor] Resampling from {orig_sr} Hz to {target_sr} Hz")
        
        resampled = librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
        
        return resampled
    
    def trim_silence(
        self,
        audio: np.ndarray,
        sr: int,
        top_db: int = 30,
        frame_length: int = 2048,
        hop_length: int = 512
    ) -> np.ndarray:
        print("[AudioProcessor] Trimming silence")
        
        trimmed, _ = librosa.effects.trim(
            audio,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length
        )
        
        print(f"[AudioProcessor] Trimmed from {len(audio)} to {len(trimmed)} samples")
        
        return trimmed
