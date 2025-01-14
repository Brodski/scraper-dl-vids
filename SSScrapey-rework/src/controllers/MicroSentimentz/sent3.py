import torchaudio
import torch
import noisereduce as nr
from scipy.signal import butter, filtfilt
import torch.nn.functional as F
from torch import nn
import soundfile as sf
from denoiser import pretrained
from denoiser.enhance import enhance

from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import time


#pip install noisereduce
#pip install denoiser

##################################
#
# soundfile
# 
# start = time.perf_counter()
# audio, rate = sf.read("outfile10k.opus")
# reduced_noise = nr.reduce_noise(y=audio, sr=rate)
# sf.write("clean_audio_SF.wav", reduced_noise, rate)
# end = time.perf_counter()
# print(f"Time SF: {end - start:.4f} seconds")


#####################################
#
# facebook's denoiser
#
def facebook_denoiser():
    start = time.perf_counter()

    model = pretrained.dns64()
    wav, sr = torchaudio.load("outfile10k.opus")
    # wav, sr = torchaudio.load("outfileFULL.opus")

    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0, keepdim=True)
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        wav = resampler(wav)
        sr = 16000

    wav = wav.squeeze(0).unsqueeze(0)
    with torch.no_grad():
        enhanced = model(wav)

    if enhanced.dim() == 3:
        enhanced = enhanced.squeeze(0)

    torchaudio.save("enhanced_audio.wav", enhanced, sr)

    end = time.perf_counter()
    print(f"Time FB save : {end - start:.4f} seconds")


def chunks_fb_denoiser():
    print("torch.cuda.is_available()", torch.cuda.is_available())
    print("torch.__version__", torch.__version__)  # Should show +rocm if using ROCm build
    print("torch.version.hip", torch.version.hip)  # Should return version if using ROCm
    start = time.perf_counter()

    def process_in_chunks(wav, model, minutes=5):  # 10 seconds at 16kHz
        chunk_size = 16000 * minutes * 60
        
        results = []
        total_length = wav.shape[1]    

        print("    total_length", total_length)
        print("    chunk_size", chunk_size)
        for i in range(0, total_length, chunk_size):
            print("\n    ", i, "running loop....")
            end = min(i + chunk_size, total_length)
            chunk = wav[:, i:end] # Make sure we don't go past the end of the audio
            print("    chunk:", chunk)
            print("    i:end", i, end)
            with torch.no_grad():
                enhanced_chunk = model(chunk)
            results.append(enhanced_chunk)
            print(f"\nShapes of all results:")
            for idx, r in enumerate(results):
                print(f"    Result {idx} shape: {r.shape}")

        print("Trying dim=2...")
        return torch.cat(results, dim=2) # dim=2 -> tells which axis to join the tensors along, eg results[0].shape -> torch.Size([1, 1, 4800000]) -> adds the 2nd dimensions, @ 4800000


    wav, sr = torchaudio.load("outfileFULL.opus")
    # wav, sr = torchaudio.load("outfile10k.opus")
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0, keepdim=True)
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        wav = resampler(wav)
        sr = 16000

    wav = wav.squeeze(0).unsqueeze(0)
    model = pretrained.dns64()
    enhanced = process_in_chunks(wav, model)
    if enhanced.dim() == 3:
        enhanced = enhanced.squeeze(0)

    torchaudio.save("enhanced_audioLoopy.wav", enhanced, sr)
    end = time.perf_counter()
    print(f"Time FB loopy : {end - start:.4f} seconds")


chunks_fb_denoiser()