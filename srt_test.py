from moviepy.editor import *
 
# File paths
audio_path = 'output.mp3'
subtitle_path = 'VIDEO_FILENAME.srt'
output_video_path = 'output.mp4'
 
audio = AudioFileClip(audio_path)
 
subtitles = []
with open(subtitle_path, 'r', encoding='utf-8') as file:
    subtitle_lines = file.read().strip().split('\n\n')
    for line in subtitle_lines:
        parts = line.strip().split('\n')
        if len(parts) >= 3:
            start, end = parts[1].split(' --> ')
            text = '\n'.join(parts[2:])
            subtitles.append((start, end, text))
 
 
video_clips = []
 
for i, subtitle in enumerate(subtitles):
    start, end, text = subtitle
    txt_clip = TextClip(text, fontsize=120, color='white')
    txt_clip = txt_clip.set_start(start).set_end(end)
 
    video_clips.append(txt_clip)
 
# Concatenate all clips into a single video
final_video = concatenate_videoclips(video_clips, method="compose", bg_color=None, padding=0)
 
# Set audio for the final video
final_video = final_video.set_audio(audio)
 
# Write the video file
final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                            remove_temp=True, fps=15)