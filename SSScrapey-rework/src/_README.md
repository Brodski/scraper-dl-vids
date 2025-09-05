




#FAST GPT
ffmpeg -i input.mp4 \
ffmpeg -i concfrag_0q_1_noaudioEnd_of_Season_Climb_I_must_not_give_up.mp4 -c:a libopus -ac 1 -ar 16000 -b:a 10k -vbr constrained -compression_level 5 -af aresample=resampler=swr:filter_size=16 -threads 4 fast_gpt.opus

#best ffmpeg
ffmpeg -i concfrag_0q_1_noaudioEnd_of_Season_Climb_I_must_not_give_up.mp4 -c:a libopus -ac 1 -ar 16000 -b:a 10k -vbr constrained -application voip  -compression_level 5 fast_gpt_5_voip_def.opus

# best yt-dlp
yt-dlp --audio-quality 0 --output "concfrag_0q_1_noaudioexract%(title)s.%(ext)s" --restrict-filenames --force-overwrites --no-continue --no-simulate --format worst --concurrent-fragments 16 "https://www.twitch.tv/videos/2549168663"




# nvidia 
pip install torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128 --extra-index-url https://pypi.org/simple

import torch
print(torch.__version__, torch.version.cuda)     # expect 2.7.0 12.8
print(torch.cuda.get_device_name(0))             # NVIDIA GeForce RTX 5080
print(torch.cuda.get_device_capability(0))       # (12, 0)





###### PREPER ######
.\venvFaster\Scripts\activate
 python .\kickPreper.py


###### DOWNLOADER ######
.\venvFaster\Scripts\activate
python .\kickDownloader  --quick-dl


###### TRANSCRIBER ######
.\venvFaster\Scripts\activate
python .\kickTranscriber
