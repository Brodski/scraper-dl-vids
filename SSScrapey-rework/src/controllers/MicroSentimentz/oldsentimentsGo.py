import json
import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_LOCAL_MODE"] = "1"  # Force local mode, no symlinks
os.environ["TRANSFORMERS_USE_SYMLINKS"] = "0"  # Belt and suspenders approach

import torch
import subprocess
# from speechbrain.pretrained import EncoderClassifier
# from speechbrain.inference import EncoderClassifier
# from speechbrain.utils.fetching import fetch, LocalStrategy
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline
from pathlib import Path
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import soundfile
# from asteroid.models import BaseModel
import torchaudio
import torch
# import torch_directml 



import torch
import torchaudio
import numpy as np

# os.environ['TRANSFORMERS_CACHE'] = './my_custom_model_directory'
# pip install speechbrain transformers torch
 
# # Load the pretrained emotion recognition model
# classifier = EncoderClassifier.from_hparams(source="speechbrain/emotion-recognition", savedir="tmpdir")

# # https://www.youtube.com/watch?v=MGBeCk6eRAw

# # Classify an audio file
# audio_file = "audio_sample.wav"
# classification = classifier.classify_file(audio_file)

# # Print the results
# print("Predicted Emotion:", classification[0])
# print("Confidence Scores:", classification[1])


# ANOTHER_DAY_EXCELLENT_TELLS_FUTURE_INBOUD_beep_beep_BOOOM_GOTS_GET_BUD_THAT_EASY_wow_so_much_swaggy_and_cooled_on_here_._THANK-v2343565421.mp3
# ffmpeg -y -i  infile -c:a libopus -ac 1 -ar 16000 -b:a 10K -vbr constrained outfile.opus
# yt-dlp "https://www.twitch.tv/videos/2343565421"  --dump-json --output '%(title)s-%(id)s.%(ext)s' --extract-audio --force-overwrites --no-continue --format worst --no-simulate --audio-format mp3 --restrict-filenames --downloader ffmpeg --audio-quality 0 --downloader-args "ffmpeg_i: -ss 00 -to 669"   
  

# emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"

#  python -m pip install torch --index-url https://download.pytorch.org/whl/cu124
#  python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cu124
#  pip install soundfile

class AudioEmotionAnalyzer:
    def __init__(self, cache_dir="./emotion_model_cache"):


        # self.device = torch_directml.device()
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = 'cpu'
        self.model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
        # self.model_name = "harshit345/wav2vec2-large-xlsr-53-ravdess-emotional-speech-recognition"
        cache_dir = "./model_directory"


        # Initialize without symlinks
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(
            self.model_name,
            cache_dir=cache_dir,
            local_files_only=False,
        )
        self.model = AutoModelForAudioClassification.from_pretrained(
            self.model_name,
            cache_dir=cache_dir,
            local_files_only=False,
        ).to(self.device)
        self.emotions = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        print("---------")
        print("---------")
        print("---------")

    def analyze_emotion(self, audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = waveform.to(self.device)  # Move to DirectML device
        chunk_seconds = 60 

        print("audio_path", audio_path)
        print("audio_path", audio_path)
        print("audio_path", audio_path)
        # print("Current directory:", os.getcwd())
        # print("WAV files found:", [f for f in os.listdir() if (f.endswith('.wav') or f.endswith('.opus'))])
        print(torchaudio.__version__)
        print("Available backends:",     torchaudio.list_audio_backends())
        print(f"PyTorch version:         {torch.__version__}") # PyTorch version: 2.5.1+cu124
        print(f"Torchaudio version:      {torchaudio.__version__}") # Torchaudio version:   2.5.1+cu124
        print(f"CUDA available:          {torch.cuda.is_available()}") # CUDA available: True
        print(f"Device:                  {self.device}") # Device: cuda
        print()
        print(f"Shape of waveform: {waveform.shape}")
        print(f"Sample rate: {sample_rate}")
        print(f"Length in seconds: {waveform.shape[1] / sample_rate}")
        print()
        print()

        if waveform.shape[0] > 1: # Convert to mono if stereo
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        if sample_rate != 16000: # Resample if needed (model expects 16kHz)
            resampler = torchaudio.transforms.Resample(sample_rate, 16000).to(self.device)
            waveform = resampler(waveform)
            sample_rate = 16000

        chunk_samples = chunk_seconds * sample_rate
        total_samples = waveform.shape[1]
        chunk_results = []

        for start_idx in range(0, total_samples, chunk_samples):
            end_idx = min(start_idx + chunk_samples, total_samples)
            chunk = waveform[:, start_idx:end_idx]

            print("total_samples:", total_samples)
            print("start_idx:", start_idx)
            print("end_idx:", end_idx)
            inputs = self.feature_extractor(
                # chunk.cpu().squeeze().numpy(),
                chunk.squeeze().numpy(),
                sampling_rate=16000,
                return_tensors="pt"
            ).to(self.device)

            torch.cuda.empty_cache()
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1)[0]
            chunk_result = {
                'start_time': start_idx / sample_rate,
                'end_time': end_idx / sample_rate,
                'predicted_emotion': self.emotions[torch.argmax(scores).item()],
                'confidence_scores': {
                    emotion: score.item()
                    for emotion, score in zip(self.emotions, scores)
                }
            }
            chunk_results.append(chunk_result)
            print("chunk_result")
            print(chunk_result)
            print()
            print()
            print()
        
        return chunk_results

def main():
    analyzer = AudioEmotionAnalyzer()
    audio_file = "outfile10k.opus"
    # audio_file = "outfile10k_short.opus"
    audio_file = "outfileFULL_enhanced.wav"
    
    results = analyzer.analyze_emotion(audio_file)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    # analyze_emotions(file_name)
    main()
    
    # emotion_recognizer = EmotionRecognizer()
    # audio_path = "path/to/your/audio.wav"
    # result = emotion_recognizer.process_audio(audio_path)
    # print(f"Emotion Analysis Results for {audio_path}:")
    # print(f"Predicted Emotion: {result['predicted_emotion']}")
    # print("\nProbabilities:")
    # for emotion, prob in result['probabilities'].items():
    #     print(f"{emotion}: {prob:.3f}")
