from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_audioclips,
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
    CompositeAudioClip,
)
import speech_recognition as sr
from pydub import AudioSegment
import speech_recognition as sr
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, clips_array
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import assemblyai as aai
import proglog


def split_temp(text, max_length=200):
    segments = []
    current_segment = ""

    words = text.split()

    for word in words:
        if len(current_segment) + len(word) + 1 <= max_length:
            if current_segment:
                current_segment += " "
            current_segment += word
        else:
            segments.append(current_segment)
            current_segment = word

    if current_segment:
        segments.append(current_segment)

    return segments


def convert_to_wav(input_audio_file, output_wav_file):
    audio = AudioSegment.from_file(input_audio_file, format="mp3")
    audio.export(output_wav_file, format="wav")


def captions(audio_file_path, key):
    output_file_path = "cache//transcriptions.txt"
    config = aai.TranscriptionConfig(
        punctuate=False,
        format_text=False,
    )
    aai.settings.api_key = key
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file_path, config=config)

    threshold_duration_ms = 200

    current_segment = []
    current_start = None
    current_end = None
    additional_offset_ms = 0
    offset_ms = transcript.words[0].start

    adjusted_segments = []

    for word in transcript.words:
        word.start -= offset_ms + additional_offset_ms
        word.end -= offset_ms + additional_offset_ms

        if current_start is None:
            current_start = word.start
        current_end = word.end

        if current_end > word.start:
            current_end = word.start

        if current_end - current_start > threshold_duration_ms:
            adjusted_text = " ".join([word.text for word in current_segment])

            adjusted_segments.append(
                {"text": adjusted_text, "start": current_start, "end": current_end}
            )

            current_segment = [word]
            current_start = word.start
            current_end = word.end
        else:
            current_segment.append(word)

    if current_segment:
        adjusted_text = " ".join([word.text for word in current_segment])

        adjusted_segments.append(
            {"text": adjusted_text, "start": current_start, "end": current_end}
        )

    text = "\n".join([segment["text"] for segment in adjusted_segments])

    adjusted_segments[0]["start"] = 0
    with open(output_file_path, "w") as output_file:
        for segment in adjusted_segments:
            section_text = (
                f"{segment['start']/1000}~{segment['end']/1000}~{segment['text']}"
            )
            output_file.write(section_text + "\n")


def combine_audio_files(list):
    final_audio = []
    bypass_first = True
    for list_val in list:
        audio_clip = AudioFileClip(list_val)

        final_audio.append(audio_clip)
    combined_audio = concatenate_audioclips(final_audio)
    combined_audio.write_audiofile(
        "cache\\Story_output.mp3",
        codec="mp3",
        logger=proglog.TqdmProgressBarLogger(print_messages=False),
    )


def adujst_vid_size(video_path):
    video_clip = VideoFileClip(video_path)

    width, height = video_clip.size
    aspect_ratio = width / height

    tolerance = 0.01
    desired_aspect_ratio = 9 / 16
    is_desired_aspect_ratio = abs(aspect_ratio - desired_aspect_ratio) < tolerance

    if is_desired_aspect_ratio is False:
        video_clip = video_clip.set_audio(None)
        desired_aspect_ratio = (9, 16)
        original_width, original_height = video_clip.size
        crop_height = int(width * desired_aspect_ratio[1] // desired_aspect_ratio[0])
        resized_clip = video_clip.resize(height=crop_height)

        return video_path
    else:
        return video_path


def set_title_start(video_path, audio_path, image_path, rest_audio):
    video = VideoFileClip(video_path)

    audio = AudioFileClip(audio_path)
    audio2 = AudioFileClip(rest_audio)
    audio_final = concatenate_audioclips([audio, audio2])

    image_clip = ImageClip(image_path)

    scaling_factor = 0.2
    image_duration = audio.duration

    image_clip = image_clip.resize(height=int(video.h * scaling_factor))

    x_center = (video.w - image_clip.w) // 2
    y_center = (video.h - image_clip.h) // 2

    image_clip = image_clip.set_position((x_center, y_center)).set_duration(
        image_duration
    )
    final_clip = CompositeVideoClip([video.set_audio(audio_final), image_clip])
    return final_clip


def add_captions(video_clip, audio_file_path, output_video_path):
    audio_clip = AudioFileClip(audio_file_path)

    transcriptions_file_path = "cache\\transcriptions.txt"
    transcriptions = []

    with open(transcriptions_file_path, "r") as transcriptions_file:
        for line in transcriptions_file:
            transcriptions.append(line)

    text_clips = []

    font = "title_image_data\\Stilu-Bold.otf"
    video_width, video_height = video_clip.size
    font_size = ((video_height * 5) // 100) + 5

    font_color = "white"
    text_start_offset = audio_clip.duration

    for transcription in transcriptions:
        font_size = (video_height * 5) // 100
        start_end, text = transcription.rsplit("~", 1)
        start, end = start_end.split("~")

        start_time = float(start)
        end_time = float(end)

        shadow_offset = (15, -15)
        shadow_color = "black"

        text_clip = TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            font=font,
            stroke_color="black",
            stroke_width=5,
        )
        zoom_factor = 0.03
        original_position = "center"

        center_x = video_width / 2
        center_y = video_height / 2

        text_width = text_clip.size[0]
        text_height = text_clip.size[1]

        text_x = center_x - text_width / 2
        text_y = center_y - text_height / 2
        shadow_offset = (10, 10)

        shadow_clip = TextClip(text, font=font, fontsize=font_size, color=shadow_color)
        shadow_clip = (
            shadow_clip.set_duration(end_time - start_time)
            .set_position((text_x + shadow_offset[0], text_y + shadow_offset[1]))
            .set_start(start_time + text_start_offset)
        )

        text_clip = (
            text_clip.set_duration(end_time - start_time)
            .set_position(original_position)
            .set_start(start_time + text_start_offset)
        )
        text_clip = zoom_text(
            (end_time - start_time) / 2, text_clip, zoom_factor, original_position
        )

        if transcription == transcriptions[-1]:
            shadow_clip = shadow_clip.set_end(end_time + text_start_offset + 1)
            text_clip = text_clip.set_end(end_time + text_start_offset + 1)

        text_clips.append(shadow_clip)
        text_clips.append(text_clip)

    video_clip = video_clip.subclip(0, end_time + text_start_offset + 1)

    composite_video = CompositeVideoClip([video_clip] + text_clips)

    composite_video.write_videofile(
        output_video_path,
        threads=4,
        codec="libx264",
        fps=60,
        logger=proglog.TqdmProgressBarLogger(print_messages=False),
    )
    print("Video Uploaded to: {}".format(output_video_path))


def zoom_text(t, text_clip, zoom_factor, original_position):
    zoomed_clip = text_clip.resize(lambda t: 1 + zoom_factor * t)
    zoomed_clip = zoomed_clip.set_position(original_position)
    return zoomed_clip
