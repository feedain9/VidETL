from pipeline.video_pipeline import VideoEditingPipeline
from editors.clipping.random_clip_editor import RandomClipEditor
from editors.formatting.aspect_ratio_format_editor import AspectRatioFormatter
from editors.captioning.caption_adder import CaptionAdder

from pipeline.pipeline_execute import execute_pipeline_from_dir
from utils.video_utils import match_and_combine_clips
from io_files.video_writer import save_video_files


# Create pipeline
pipeline = VideoEditingPipeline()

# Add tasks
<<<<<<< HEAD
pipeline.add_task(RandomClipEditor(0, 71))
pipeline.add_task(AspectRatioFormatter('9:16'))
pipeline.add_task(CaptionAdder(caption_font=r"C:\Users\armen\Documents\github\VidETL\assets\Montserrat-ExtraBold.ttf",caption_fontsize=100))

directory = "example_videos\example_samples"
for filename in os.listdir(directory):
    if filename.endswith(".mp4"):

        unique_id = int(time.time())
        # Load the original video clip
        original_video = VideoFileClip(os.path.join(directory, filename))
        # Execute pipeline on video
        filename = filename.split(".mp4")[0]
        final_clipped_video = pipeline.execute(original_video)
        output_filename = f"{filename}_clip_{unique_id}.mp4"
        final_clipped_video.write_videofile(output_filename, codec="libx264", fps=24, audio_codec='aac')
=======
pipeline.add_task(RandomClipEditor(0, 20))
pipeline.add_task(AspectRatioFormatter('8:9'))
pipeline.add_task(CaptionAdder())

directory = "../example_videos/example_samples"
top_clips = execute_pipeline_from_dir(directory, pipeline)

# Seperate pipeline for bottom clips
bottom_pipeline = VideoEditingPipeline()
bottom_pipeline.add_task(RandomClipEditor(0, 20, silent=True))
bottom_pipeline.add_task(AspectRatioFormatter('8:9'))
>>>>>>> 805f1fe5e70ec32973bc55b5dc690a0c18e9b1f8

bottom_dir = "../example_videos/bottom"
bottom_clips = execute_pipeline_from_dir(bottom_dir, bottom_pipeline)

# Combine clips top/bottom util function
combined_clips = match_and_combine_clips(top_clips, bottom_clips)

# Save files util function (to move to io)
save_video_files(combined_clips, "../output")
