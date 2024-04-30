from moviepy.editor import TextClip, CompositeVideoClip
import time, os
from utils.audio_utils import extract_audio, generate_captions

class CaptionAdder:
    def __init__(self, caption_font='Arial', caption_fontsize=48, caption_color='white'):
        self.caption_font = caption_font
        self.caption_fontsize = caption_fontsize
        self.caption_color = caption_color

    def get_caption_json(self, video_clip):
        unique_id = int(time.time()) 
        audio_filename = f"output_{unique_id}.wav"
        # Assuming the add_captions method applies captions to the clip and returns the modified clip
        extract_audio(video_clip, audio_filename)
        caption_json = generate_captions(audio_filename)
        with open(r"C:\Users\armen\Documents\github\VidETL\SrtFiles\captions.json", "w") as f:
            f.write(str(caption_json))
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        return caption_json

    def apply(self, video_clip):
        clips = [video_clip]  # Start with the original clip
<<<<<<< HEAD
        # caption_json = self.get_caption_json(video_clip)
        with open(r"C:\Users\armen\Documents\github\VidETL\SrtFiles\captions.json", "r") as f:
            caption_json = eval(f.read())
=======
        caption_json = self.get_caption_json(video_clip)
        video_width, video_height = video_clip.size

        # Reference dimensions (e.g., 640x720)
        ref_width, ref_height = 640, 720

        # Calculate the scaling factor based on width (or height)
        scale_factor = video_width / ref_width

        # Adjust font size based on the scaling factor
        adjusted_fontsize = int(self.caption_fontsize * scale_factor)
>>>>>>> 805f1fe5e70ec32973bc55b5dc690a0c18e9b1f8

        for segment in caption_json['segments']:
            for word_info in segment['words']:
                word = word_info['text']
                if word_info["confidence"] < 0.2:
                    word = "null"
                    print(word_info["confidence"])

                start_time = word_info['start']
                end_time = word_info['end']

<<<<<<< HEAD
                # Create a TextClip for each word
                txt_clip = TextClip(word, fontsize=self.caption_fontsize, font=self.caption_font, color=self.caption_color)
                txt_clip = txt_clip.set_pos('center').set_start(start_time).set_duration(end_time - start_time)

                outline_txt = TextClip(word, fontsize=self.caption_fontsize+2, font=self.caption_font, color="black")
                outline_txt_clip = outline_txt.set_pos('center').set_start(start_time).set_duration(end_time - start_time)

=======
                # Create a TextClip for each word with adjusted fontsize
                txt_clip = TextClip(word, fontsize=adjusted_fontsize, font=self.caption_font, color=self.caption_color, size=(video_width*1/2, None), bg_color='black', method='caption')
                txt_clip = txt_clip.set_pos('bottom').set_start(start_time).set_duration(end_time - start_time)

>>>>>>> 805f1fe5e70ec32973bc55b5dc690a0c18e9b1f8
                # Add the text clip to the list of clips
                clips.append(txt_clip)

        # Composite all clips (original and text clips) together
        video_with_captions = CompositeVideoClip(clips)

        return video_with_captions
