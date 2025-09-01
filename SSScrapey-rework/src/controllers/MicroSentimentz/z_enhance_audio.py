import os
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
# def facebook_denoiser():
#     start = time.perf_counter()

#     model = pretrained.dns64()
#     wav, sample_rate = torchaudio.load("outfile10k.opus")
#     # wav, sample_rate = torchaudio.load("outfileFULL.opus")

#     if wav.shape[0] > 1:
#         wav = torch.mean(wav, dim=0, keepdim=True)
#     if sample_rate != 16000:
#         resampler = torchaudio.transforms.Resample(sample_rate, 16000)
#         wav = resampler(wav)
#         sample_rate = 16000

#     wav = wav.squeeze(0).unsqueeze(0)
#     with torch.no_grad():
#         enhanced = model(wav)

#     if enhanced.dim() == 3:
#         enhanced = enhanced.squeeze(0)

#     torchaudio.save("enhanced_audio.wav", enhanced, sample_rate)

#     end = time.perf_counter()
#     print(f"Time FB save : {end - start:.4f} seconds")


def process_in_chunks(wav, model, minutes=5):  # 10 seconds at 16kHz
    start = time.perf_counter()
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
        time_diff_print(start)

    print("Trying dim=2...")
    return torch.cat(results, dim=2) # dim=2 -> tells which axis to join the tensors along, eg results[0].shape -> torch.Size([1, 1, 4800000]) -> adds the 2nd dimensions, @ 4800000

def time_diff_print(start):
    end = time.perf_counter()
    return f"{end - start:.4f}"

def chunks_fb_denoiser(audio_before):
    start = time.perf_counter()

    # Setup names
    # name, extension = os.path.splitext(audio_before)
    audio_after = audio_before.rsplit('.', 1)[0] + '_enhanced.wav'

    # Do the magic
    wav, sample_rate = torchaudio.load(audio_before)
    
    if wav.shape[0] > 1: # If stero, convert to mono
        wav = torch.mean(wav, dim=0, keepdim=True)
    if sample_rate != 16000: # code soon after expects 16kHz
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        wav = resampler(wav)
        sample_rate = 16000

    wav = wav.squeeze(0).unsqueeze(0) #  tensor shape/dimensions ... science stuff
    model = pretrained.dns64()
    enhanced = process_in_chunks(wav, model)
    if enhanced.dim() == 3:
        enhanced = enhanced.squeeze(0)

    # Save & return
    # torchaudio.save("enhanced_audioLoopy.wav", enhanced, sample_rate)
    torchaudio.save(audio_after, enhanced, sample_rate)
    audio_enhanced_abs_path = os.path.abspath(audio_after)

    print(f"Time FB loopy : {time_diff_print(start)} seconds")
    print("Saved enhanced file @", audio_enhanced_abs_path)
    return audio_enhanced_abs_path


filename = "_egirl_hq.wav"
filename = "_gura.wav"
chunks_fb_denoiser(filename)