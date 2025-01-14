from transformers import (AutoModelForAudioClassification, Wav2Vec2ForCTC)

# 
# --> ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition
#     Model's label mapping:
#     {0: 'angry', 1: 'calm', 2: 'disgust', 3: 'fearful', 4: 'happy', 5: 'neutral', 6: 'sad', 7: 'surprised'}

# --> harshit345/xlsr-wav2vec-speech-emotion-recognition
#     Model's label mapping:
#     {0: 'anger', 1: 'disgust', 2: 'fear', 3: 'happiness', 4: 'sadness'}

# --> audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim
#     Model's label mapping:
#     {0: 'arousal', 1: 'dominance', 2: 'valence'}

# --> facebook/wav2vec2-base-960h
#     Model's label mapping:
#     {0: 'LABEL_0', 1: 'LABEL_1'}

# --> jonatasgrosman/wav2vec2-large-xlsr-53-english
#     Model's label mapping:
#     {0: 'LABEL_0', 1: 'LABEL_1'}

# --> superb/wav2vec2-base-superb-er
#     Model's label mapping:
#     {0: 'neu', 1: 'hap', 2: 'ang', 3: 'sad'}


# model = AutoModelForAudioClassification.from_pretrained("facebook/wav2vec2-base-960h")
# model = AutoModelForAudioClassification.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-english")
# model =  
# model = Wav2Vec2ForCTC.from_pretrained("MIT/ast-finetuned-speech-commands-v2")
# model = Wav2Vec2ForCTC.from_pretrained("microsoft/wavlm-base-plus-sv")
# model = Wav2Vec2ForCTC.from_pretrained("antonxon/wav2vec2-base-iemocap-5emotions")
# model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-xlsr-53")
# model = Wav2Vec2ForCTC.from_pretrained("superb/wav2vec2-base-superb-er")
model = Wav2Vec2ForCTC.from_pretrained("speechbrain/emotion-recognition-wav2vec2-IEMOCAP")
print("Model's label mapping:")
print(model.config.id2label)