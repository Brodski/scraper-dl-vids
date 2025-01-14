from asteroid.models import BaseModel
import torch
import torchaudio
from transformers import pipeline

class VoiceEmotionAnalyzer:
    def __init__(self):
        # Using the verified model for voice separation
        # self.voice_filter = BaseModel.from_pretrained("mpariente/ConvTasNet_WHAM_sepclean")
        # self.voice_filter = BaseModel.from_pretrained("JorisCos/ConvTasNet_Libri2Mix_sepclean_16k")
        self.voice_filter = BaseModel.from_pretrained("JorisCos/ConvTasNet_Libri3Mix_sepnoisy_16k")
        
        # Emotion classification model
        # self.emotion_classifier = pipeline(
        #     "audio-classification",
        #     model="audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
        # )

    def clean_voice(self, audio_path, output_path=None):
        print()
        print()
        print()
        # print(self.voice_filter)
        print()
        print()
        print()
        estimates = self.voice_filter.separate(audio_path, force_overwrite=True)
        # estimates = self.voice_filter.separate(audio_path, resample=True)
        
        clean_voice = estimates[0]

        if clean_voice.dim() == 3:
            clean_voice = clean_voice.squeeze(0)
        
        # Save the cleaned voice if output path is provided
        if output_path:
            torchaudio.save(
                output_path,
                clean_voice.cpu(),  # Ensure tensor is on CPU
                16000              # Fixed sample rate of 16kHz
            )
        
        return clean_voice

    def analyze_emotion(self, audio_path, clean_first=True):
        """
        Analyze emotions in speech, with optional cleaning
        """
        if clean_first:
            # Clean the voice first
            clean_voice = self.clean_voice(audio_path)
            # Analyze emotions in cleaned voice
            emotions = self.emotion_classifier(clean_voice)
        else:
            # Analyze original audio directly
            emotions = self.emotion_classifier(audio_path)
            
        return emotions

# Example usage
def process_audio_file(input_path, output_path=None):
    """Process an audio file and show emotion analysis results"""
    analyzer = VoiceEmotionAnalyzer()
    
    if output_path:
        print(f"Cleaning voice and saving to {output_path}")
        analyzer.clean_voice(input_path, output_path)
    
    print("Analyzing emotions in the speech...")
    emotions = analyzer.analyze_emotion(input_path)
    
    print("\nEmotion Analysis Results:")
    for emotion in emotions:
        print(f"Emotion: {emotion['label']}")
        print(f"Confidence: {emotion['score']:.2%}")

# Use it like this:
if __name__ == "__main__":
    input_file = "noisy_speech.wav"
    input_file = "outfile10k.opus"
    output_file = "clean_speech.wav"
    process_audio_file(input_file, output_file)