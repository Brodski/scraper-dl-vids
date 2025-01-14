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
from asteroid.models import BaseModel
import torchaudio
import torch



import torch
import torchaudio


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


# def goSentiments(isDebug=False):
#     pass


# ANOTHER_DAY_EXCELLENT_TELLS_FUTURE_INBOUD_beep_beep_BOOOM_GOTS_GET_BUD_THAT_EASY_wow_so_much_swaggy_and_cooled_on_here_._THANK-v2343565421.mp3
# ffmpeg -y -i  infile -c:a libopus -ac 1 -ar 16000 -b:a 10K -vbr constrained outfile.opus
# yt-dlp "https://www.twitch.tv/videos/2343565421"  --dump-json --output '%(title)s-%(id)s.%(ext)s' --extract-audio --force-overwrites --no-continue --format worst --no-simulate --audio-format mp3 --restrict-filenames --downloader ffmpeg --audio-quality 0 --downloader-args "ffmpeg_i: -ss 00 -to 669"   
  



# class EmotionRecognizer:
#     def __init__(self):
#         pass
#     def process_audio(self, audio_path):  # Returns: dict: Dictionary containing emotion probabilities and predicted emotion
#         classifier = EncoderClassifier.from_hparams(
#             source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
#             savedir="pretrained_models/emotion-recognition-wav2vec2-IEMOCAP"
#         )
#         emotion_labels = { 0: "angry", 1: "happy", 2: "neutral", 3: "sad" }

#         signal, fs = torchaudio.load(audio_path)
        
#         # Ensure audio is mono and at correct sample rate (16kHz for wav2vec2)
#         if signal.shape[0] > 1:
#             signal = torch.mean(signal, dim=0, keepdim=True)

#         if fs != 16000:
#             resampler = torchaudio.transforms.Resample(fs, 16000)
#             signal = resampler(signal)

#         embeddings = classifier.encode_batch(signal)
#         predictions = classifier.mods.classifier(embeddings)

#         # Convert predictions to probabilities
#         probs = torch.softmax(predictions[0], dim=0)
#         predicted_emotion = emotion_labels[torch.argmax(probs).item()]
#         results = {
#             "predicted_emotion": predicted_emotion,
#             "probabilities": {
#                 emotion: prob.item()
#                 for emotion, prob in zip(emotion_labels.values(), probs)
#             }
#         }
#         return results

# emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"


class AudioEmotionAnalyzer:
    def __init__(self, cache_dir="./emotion_model_cache"):
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
        )
        self.emotions = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']

#  pip install torch --index-url https://download.pytorch.org/whl/cu124
#  pip install torchaudio --index-url https://download.pytorch.org/whl/cu124
#  pip install soundfile
    def analyze_emotion(self, audio_path):
        print("audio_path", audio_path)
        print("audio_path", audio_path)
        print("audio_path", audio_path)
        print("audio_path", audio_path)
        print("Current directory:", os.getcwd())
        print("WAV files found:", [f for f in os.listdir() if (f.endswith('.wav') or f.endswith('.opus'))])
        print(torchaudio.__version__)
        print("Available backends:",     torchaudio.list_audio_backends())
        print(f"PyTorch version:         {torch.__version__}")
        print(f"Torchaudio version:      {torchaudio.__version__}")
        print(f"CUDA available:          {torch.cuda.is_available()}")
        print()
        print()
        print()
            
        # waveform, sample_rate = torchaudio.load(
        #     'outfile10k.opus',
        #     format="opus",
        #     # decoder="ffmpeg"  # Explicitly specify ffmpeg decoder
        # )
        
        # waveform, sample_rate = torchaudio.load('outfile10k.opus', format="opus", channels_first=False)
        waveform, sample_rate = torchaudio.load(audio_path)
        print(f"Shape of waveform: {waveform.shape}")
        print(f"Sample rate: {sample_rate}")
        print(f"Length in seconds: {waveform.shape[1] / sample_rate}")
        
        # Resample if needed (model expects 16kHz)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Extract features
        inputs = self.feature_extractor(
            waveform.squeeze().numpy(),
            # sampling_rate=sample_rate,
            sampling_rate=16000,
            return_tensors="pt"
        )
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)[0]
            
        results = {
            'predicted_emotion': self.emotions[torch.argmax(scores).item()],
            'confidence_scores': {
                emotion: score.item()
                for emotion, score in zip(self.emotions, scores)
            }
        }
        
        return results

def main():
    # Example usage
    analyzer = AudioEmotionAnalyzer()
    audio_file = "outfile10k.opus"
    audio_file = "outfile10k_short.opus"
    audio_file = "bullshit.mp3"
    
    try:
        results = analyzer.analyze_emotion(audio_file)
        print(f"Predicted Emotion: {results['predicted_emotion']}")
        print("\nConfidence Scores:")
        
        # Sort emotions by confidence score
        sorted_emotions = sorted(
            results['confidence_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for emotion, score in sorted_emotions:
            print(f"{emotion}: {score:.3f}")
            
    except Exception as e:
        print(f"Error: {str(e)}")


def separate_and_save_voice(input_audio_path, output_voice_path, output_background_path=None):
    # Load our voice separation model
    # voice_filter = BaseModel.from_pretrained("JorisCos/ConvTasNet_WHAM_sepclean")
    voice_filter = BaseModel.from_pretrained("JorisCos/ConvTasNet_Libri2Mix_sepclean_16k")

    estimates = voice_filter.separate_file(input_audio_path)

    voice = estimates[0]
    
    if voice.dim() == 3:
        voice = voice.squeeze(0) 
    torchaudio.save(
        output_voice_path,
        voice.cpu(),  # Ensure the tensor is on CPU
        16000  # Sample rate
    )
    if output_background_path and estimates.shape[0] > 1:
        background = estimates[1]
        if background.dim() == 3:
            background = background.squeeze(0)
        torchaudio.save(
            output_background_path,
            background.cpu(),
            16000
        )
        
    return voice

def sep_audio():
    audio_file = "outfile10k.opus"
    audio_file = "outfile10k_short.opus"
    audio_file = "bullshit.mp3"

    audio_file = "noisy_speech.wav"
    sep_voice_output = "clean_voice.wav"
    sep_background_output = "background.wav"

    # Separate and save both voice and background
    separated_voice = separate_and_save_voice(
        audio_file, 
        sep_voice_output, 
        sep_background_output
    )

    print(f"Saved cleaned voice to: {sep_voice_output}")
    print(f"Saved background audio to: {sep_background_output}")



if __name__ == "__main__":
    # analyze_emotions(file_name)
    # main()
    sep_audio()
    
    # emotion_recognizer = EmotionRecognizer()
    # audio_path = "path/to/your/audio.wav"
    # result = emotion_recognizer.process_audio(audio_path)
    # print(f"Emotion Analysis Results for {audio_path}:")
    # print(f"Predicted Emotion: {result['predicted_emotion']}")
    # print("\nProbabilities:")
    # for emotion, prob in result['probabilities'].items():
    #     print(f"{emotion}: {prob:.3f}")
