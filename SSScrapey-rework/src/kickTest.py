import datetime
import time
from typing import List
from env_file import env_varz
env_varz.init_argz()
import controllers.MicroTranscriber.transcriberGo as transcriberGo
from env_file import env_varz
from models.Vod import Vod
import controllers.MicroTranscriber.transcriber as transcriber
import controllers.MicroTranscriber.split_ffmpeg as split_ffmpeg
from models.Splitted import Splitted
from controllers.MicroTranscriber.audio2Text_faster_whisper import Audio2Text 

def getDebugVod():
    # V very shity
    tuple =  ('2668418939', 'geranimo', 'Journey to Challenger! Almost Masters Time to LOCK IN //  NA vs EU !rivality', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2069, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2026, 1, 17, 5, 37), 'channels/vod-audio/geranimo/2668418939/Journey_to_Challenger_Almost_Masters_Time_to_LOCK_IN_NA_vs_EU_rivality-v2668418939.opus', '-1', 'English')
    tuple =  ('v2668418939', 'geranimo', 'Journey_to_Challenger_Almost_Masters_Time_to_LOCK_IN_NA_vs_EU_rivality-v2668418939', '78', '1:18', 39744, 'https://www.twitch.tv/videos/v2668418939', datetime.datetime(2069, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2026, 1, 17, 5, 37), 'channels/vod-audio/geranimo/2668418939/Journey_to_Challenger_Almost_Masters_Time_to_LOCK_IN_NA_vs_EU_rivality-v2668418939.opus', '-1', 'English')
    Id, ChannelNameId, Title, Duration, DurationString,ViewCount,WebpageUrl,StreamDate, TranscriptStatus, Priority, Thumbnail,TodoDate,S3Audio,ChanCurrentRank,Language  = tuple
    vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=Language)
    return vod


if __name__ == "__main__":
    print("transcriberGo gogogo!")
    vod: Vod        = getDebugVod()
    start_time      = time.time()
    # metadata_       = MetadataShitty(vod=vod)

    relative_path: str = transcriber.downloadAudio(vod)

    splitted_list: List[Splitted] = split_ffmpeg.splitHugeFile(vod, relative_path)

    saved_caption_files, metadata_ = Audio2Text.doWhisperStuff(vod, splitted_list)

    end = time.time() - start_time
    print("**************************************")
    print("****                              ****")
    print("****            TIME              ****")
    print("****                              ****")
    print("**************************************")
    print(end)
    print(end)
    print(end)
    print(end)

    # C:\Users\BrodskiTheGreat\.cache\huggingface\hub\models--Systran--faster-whisper-small
    # clear out this bullshit ^ sometime
    # tiny float 187 sec ..... 8.5hours
    # tiny int 217 sec ..... 8.5hours
    # small int 312 sec
    # small float 528 sec
# yt-dlp "https://www.twitch.tv/videos/2665629308?filter=archives&sort=time" 
#   --dump-json 
#   --output "C:/Users/BrodskiTheGreat/Desktop/desktop/Code/scraper-dl-vids/SSScrapey-rework/assets/audio/%(title)s-%(id)s.%(ext)s"
#   --format worst 
#   --quiet 
#   --no-simulate 
#   --restrict-filenames 
#   --audio-quality 0 
#   --concurrent-fragments 100
