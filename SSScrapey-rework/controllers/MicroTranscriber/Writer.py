
import json
import os

class Writer:
    extension: str
    debug_print: bool

    def __init__(self, extension):
        self.extension = extension
        self.debug_print = True
        self.debug_count = 0

    def write(self, outputs, filename, directory_save):
        print(self.extension)
        print(self.extension)
        print(self.extension)
        audio_file_name = os.path.splitext(os.path.basename(filename))[0]
        subtitle_filename = f"{audio_file_name}.{self.extension}"

        json_transcript = { "segments" : [] }
        with open(directory_save + subtitle_filename, 'w') as subbed_file:
            if self.extension == "txt":
                subbed_file.write(outputs["text"].strip())
                return
            if self.extension == "vtt":
                self.write_print(subbed_file, "WEBVTT\n\n")

            prev = 0
            for index, chunk in enumerate(outputs['chunks']):
                prev, start_time = self.seconds_to_thee_time_format(prev, chunk['timestamp'][0])
                prev, end_time = self.seconds_to_thee_time_format(prev, chunk['timestamp'][1])

                if self.debug_print and self.debug_count < 20:
                    print(f"{start_time} --> {end_time}\n", end="")
                    print(f"{chunk['text'].strip()}\n\n", end="")
                    self.debug_count += 1
                    if self.debug_count == 20:
                        print("Transcripts no longer printing, view s3 for more ...")

                if self.extension == "srt":
                    subbed_file.write(f"{index + 1}\n")
                    subbed_file.write(f"{start_time} --> {end_time}\n")
                    subbed_file.write(f"{chunk['text'].strip()}\n\n")
                if self.extension == "vtt":
                    subbed_file.write(f"{start_time} --> {end_time}\n")
                    subbed_file.write(f"{chunk['text'].strip()}\n\n")
                if self.extension == "json":
                    json_transcript["segments"].append( {
                        "start": float(start_time),
                        "end": float(end_time),
                        "text": chunk['text'].strip()
                    })
                # if self.extension == "tsv":
                #     pass
            
            if self.extension == "json":
                print("WE DOING THE JSON")
                json.dump(json_transcript, subbed_file)
                print("DUMPED!")

    def write_print(self, file, txt):
        file.write(txt)
        print(txt, end="")

    def seconds_to_thee_time_format(self, prev, seconds):
        if not (isinstance(seconds, int) or isinstance(seconds, float)):
            seconds = prev
        else:
            prev = seconds
        sec_OG = seconds
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        prev_next = None
        if self.extension == "srt":
            prev_next = (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}")
        if self.extension == "vtt":
            if hours > 0:
                prev_next = (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}")
            else:
                prev_next = (prev, f"{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}")
        if self.extension == "json":
            # prev_next = (prev, f"{int(seconds)}.{milliseconds:03d}")
            prev_next = (prev, f"{int(sec_OG)}.{milliseconds:03d}")
            return (prev, sec_OG)
        return prev_next



    
