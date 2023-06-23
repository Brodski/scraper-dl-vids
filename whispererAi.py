import whisper
import whisper.utils
import time
from whisper.utils import get_writer

import os 
# from whisper import cli

def mp3Transcribe(audio_path):
    model = whisper.load_model("base")
    print ("START")
    print (audio_path)
    start_time = time.time()
    result = model.transcribe(audio_path,  fp16=False)
    run_time = time.time() - start_time 
    print("run_time=")
    print(run_time)

    output_dir = "."
    audio_basename = os.path.basename(audio_path)

    print ("output_dir: ", output_dir )
    print ("audio_path: ", audio_path)
    print ("audio_basename: ", audio_basename)

    # Save as an SRT file
    srt_writer = get_writer("srt", output_dir)
    srt_writer(result, audio_basename + ".srt")

    # Save as a VTT file
    vtt_writer = get_writer("vtt", output_dir)
    vtt_writer(result, audio_basename + ".vtt")

    # Save as a txt file
    txt_writer = get_writer("txt", output_dir)
    txt_writer(result, audio_basename + ".txt")

    # Save as json
    print(result["text"])
    return True
