# -*- coding: utf-8 -*-
import os
import time
import instaloader
import requests
import json
import shutil
import whisper
from moviepy.editor import *
import g4f
import edge_tts
import random
import asyncio
import ffmpeg
from datetime import timedelta
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip
import time, os
from pipeline.video_pipeline import VideoEditingPipeline
from editors.clipping.random_clip_editor import RandomClipEditor
from editors.formatting.aspect_ratio_format_editor import AspectRatioFormatter
from editors.captioning.caption_adder import CaptionAdder



users_to_follow = ["innovgadgetspot"]#,"ledenicheurdebonplans", "tiffanyallison7"]
time_sleep = 28800


def compress_video(video_full_path, size_upper_bound, two_pass=True, filename_suffix='cps_'):
    """
    Compress video file to max-supported size.
    :param video_full_path: the video you want to compress.
    :param size_upper_bound: Max video size in KB.
    :param two_pass: Set to True to enable two-pass calculation.
    :param filename_suffix: Add a suffix for new video.
    :return: out_put_name or error
    """
    filename, extension = os.path.splitext(video_full_path)
    extension = '.mp4'
    output_file_name = filename + filename_suffix + extension

    # Adjust them to meet your minimum requirements (in bps), or maybe this function will refuse your video!
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        probe = ffmpeg.probe(video_full_path)
        # Video duration, in s.
        duration = float(probe['format']['duration'])
        # Audio bitrate, in bps.
        audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
        # Target total bitrate, in bps.
        target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print('Bitrate is extremely low! Stop compress!')
            return False

        # Best min size, in kB.
        best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
        if size_upper_bound < best_min_size:
            print('Quality not good! Recommended minimum size:', '{:,}'.format(int(best_min_size)), 'KB.')
            # return False

        # Target audio bitrate, in bps.
        audio_bitrate = audio_bitrate

        # target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
            return False

        i = ffmpeg.input(video_full_path)
        if two_pass:
            ffmpeg.output(i, os.devnull,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                          ).overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()
        else:
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
            return output_file_name
        elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):  # Do it again
            return compress_video(output_file_name, size_upper_bound)
        else:
            return False
    except FileNotFoundError as e:
        print('You do not have ffmpeg installed!', e)
        print('You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251')
        return False
    
def send_video_to_discord_webhook(video_path, webhook_url="https://discord.com/api/webhooks/1185561806706573383/M9pavj1lZvZr9cRjm6Q3mlkbbuGQ5mx4G7fHRWfUbW51_BDr4_QQVac4YrWMfBlSNBm6"):
    # Ouvrir la vidéo en mode binaire
    with open(video_path, "rb") as file:
        # Lire le contenu de la vidéo
        video_content = file.read()

    # Préparer les données à envoyer
    files = {'file': ('video.mov', video_content)}

    # Paramètres supplémentaires (facultatif)
    params = {
        'content': 'Poste cette vidéo <@888717665659662346> !'
    }

    # Envoyer la requête POST à l'URL du webhook Discord
    response = requests.post(webhook_url, files=files, data=params)

    # Afficher la réponse (statut de la requête, contenu de la réponse)
    print(response.status_code, response.text)


def rewrite_subtitle(text):
    exemple = "{\"texte\":\"Mes meilleures idées cadeaux pour Noël\"}"
    # Définissez la question à poser à l'API GPT-4 / Je souhaite que vous agissiez en tant que journaliste. 
    prompt = f"""
            Vos réponses et les rédactions doivent contenir uniquement l'article au format JSON avec une clé : 'texte'. N'incluez aucunes explications, fournissez uniquement qu'une réponse JSON conforme à la norme RFC8259, en faisant bien attention que la réponse ne produise pas une erreur de type \"JSONDecodeError: Invalid control character\" et respectant ce format sans déviation:
            {exemple}
            Ma première demande de suggestion est : j'ai besoin que tu réécrives le contenu d'une de mes vidéos tiktok dans le même style, voici le contenu : {text}.
            """
    messages=[
            {"role": "system", "content": "Tu es assistant d'un community manager d'un compte tiktok sur des découvertes de produits sur amazon."},
            {"role": "user", "content": prompt}
        ]
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            # provider=g4f.Provider.ChatgptAi,
            messages=messages
        )
        start_index = response.find('{')
        end_index = response.rfind('}') + 1
        json_str = response[start_index:end_index].replace('\n', '')
        json_data = json.loads(json_str)
        texte = json_data["texte"]
        response = {
            "texte":texte,
        }
        return response
    except Exception:
        print(str(Exception)[:100])
        return None



async def generate_voice(text):
    final_path = r"output.mp3"
    # TEXT = """Transformez instantanément votre espace avec le Ruban LED Néon Beaeet. 3 mètres de couleurs éclatantes, contrôle via Wifi ou Alexa, synchronisation musicale, et une qualité supérieure pour une expérience LED unique. Parfait pour la chambre, le gaming, les fêtes. Laissez la magie opérer. Disponible maintenant sur Amazon."""
    voices = await edge_tts.VoicesManager.create()
    voice = voices.find(Gender="Male", Language="fr")
    communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
    await communicate.save(final_path)
    return final_path


def accelerate_audio(audio_path):
    audio = AudioFileClip(audio_path)
    audio = audio.fx(vfx.speedx, 1.15)
    audio.write_audiofile(f"accelerated_{audio_path}")
    return f"accelerated_{audio_path}"

def mute_add_audio(video_path, audio_path):
    directory, old_filename = os.path.split(video_path)
    final_video = os.path.join(directory, "output.mov")
    # Load the video
    video = VideoFileClip(video_path)
    video_intro = VideoFileClip("assets/intro.mp4")
    
    audio = AudioFileClip(audio_path)

    logo = (ImageClip("assets/lsb-modified.png")
                .set_duration(video.duration)
                .set_position(("left", "top")))

    # Remove the audio
    video_without_audio = video.without_audio()
    video_with_audio = video_without_audio.set_audio(audio)

    # Composite video with intro
    final_with_intro = concatenate_videoclips([video_intro, video_with_audio])

    final = CompositeVideoClip([final_with_intro, logo])
    
    # Write the result to a file
    final.write_videofile(final_video, codec='libx264')
    return final_video

def overlay_subtitle(video_path, subtitle_path):
    video = VideoFileClip(video_path)

    generator = lambda txt: TextClip(txt, font=r'C:\Users\armen\Documents\github\VidETL\assets\Montserrat-ExtraBold.ttf', fontsize=70, color='white', stroke_color='black', stroke_width=4, method='caption', align='South',size=((video.w//1.5,None)))
    subtitles = SubtitlesClip(subtitle_path, generator)

    result = CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])
    result.write_videofile(f"final_video.mp4", fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    return "final_video.mp4"


def add_bgmusic(video_path, audio_path=r"assets\bg_aesthetic.mp3"):
    from moviepy.audio.fx.all import volumex
    output_filename="output.mp4"
    # Load the video
    video = VideoFileClip(video_path)
    video_duration = video.duration
    audio_path = AudioFileClip(audio_path)
    new_audio = audio_path.fx(volumex, 0.05)
    final_audio = CompositeAudioClip([video.audio, new_audio])
    final_clip = video.set_audio(final_audio)
    final_clip = final_clip.set_duration(video_duration)
    final_clip.write_videofile(output_filename, codec="libx264", fps=24, audio_codec='aac')
    return output_filename

def add_subtitle(video_path, aspect_ratio, caption_fontsize):
    filename=video_path
    pipeline = VideoEditingPipeline()

    # Add tasks
    # pipeline.add_task(RandomClipEditor(0, 71))
    pipeline.add_task(AspectRatioFormatter(aspect_ratio))
    pipeline.add_task(CaptionAdder(caption_font=r"C:\Users\armen\Documents\github\VidETL\assets\Montserrat-ExtraBold.ttf",caption_fontsize=caption_fontsize))

    unique_id = int(time.time())
    # Load the original video clip
    original_video = VideoFileClip(video_path)
    # Execute pipeline on video
    filename = filename.split(".mp4")[0]
    final_clipped_video = pipeline.execute(original_video)
    output_filename = f"{filename}_clip_{unique_id}.mp4"
    final_clipped_video.write_videofile(output_filename, codec="libx264", fps=24, audio_codec='aac')
    return output_filename

def get_insta_post():
    global time_sleep
    model = whisper.load_model("base")
    # Create an instance of Instaloader class
    bot = instaloader.Instaloader()
    cookies = {
        "csrftoken":"xC0iSpxfoqkJn7qbB7l8p9MOoBoMw7np",
        "sessionid":"60607662307%3AjzAJndlqOog7Dt%3A18%3AAYdXsNUvvyljHEV9g5i4rcXhoQG2xSgozXCm08k8DQ"
    }
    bot.load_session(username="lesecteurfr", session_data=cookies)
    # bot.login(USER, PASSWORD)
    # Track user 
    for user in users_to_follow:
        profile = instaloader.Profile.from_username(bot.context, user)
        # Get all posts from the profile
        posts = profile.get_posts()
        # Iterate and download them
        for index, post in enumerate(posts, 1):
            short_code = post.shortcode
            print("shortcode:",post.shortcode)
            bot.download_post(post, target=f"{profile.username}_{index}")
            break
        
    file_path = None
    for file in os.listdir(f"innovgadgetspot_1"):
        if file.endswith(".mp4"):
            file_path = f"innovgadgetspot_1/{file}"
            video = VideoFileClip(file_path)
            video.audio.write_audiofile(f"innovgadgetspot_1/audio.mp3")
            # print("Voici la vidéo:",file)
            result = model.transcribe(f"innovgadgetspot_1/audio.mp3")
            content_video = result["text"]
            rewrited_video = rewrite_subtitle(content_video)["texte"]
            print("Original version:",content_video, "\nNew version:", rewrited_video)
            new_audio_generated = asyncio.run(generate_voice(rewrited_video))
            new_audio = accelerate_audio(new_audio_generated)
            new_video = mute_add_audio(file_path,new_audio)
            final_video = add_subtitle(new_video, "9:16", 100)
            add_music = add_bgmusic(final_video)
            new_video_compressed = compress_video(add_music, 15 * 1000)
            send_video_to_discord_webhook(new_video_compressed)
            from post_reel import post, post_insta, upload_video, delete_video
            delete_video()
            with open(f"{profile.username}_{index}", "w"):
                shutil.rmtree(f"{profile.username}_{index}")
            video_url = upload_video(new_video_compressed)
            if video_url:
                post_insta(new_video_compressed)
                print("fini!")
            return 


# get_insta_post()

add_subtitle(r"C:\Users\armen\Documents\github\VidETL\720900_court_decorassion.mp4", "4:5", 50)





# segments = model.transcribe(new_audio)
# segments = segments['segments']
# srtFilename = os.path.join("SrtFiles", f"VIDEO_FILENAME.srt")
# for segment in segments:
#     startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
#     endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
#     text = segment['text']
#     segmentId = segment['id']+1
#     segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
#     with open(srtFilename, 'a', encoding='utf-8') as srtFile:
#         srtFile.write(segment)