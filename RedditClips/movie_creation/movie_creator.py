from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_audioclips,
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
)
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
import numpy as np
import csv
from spellchecker import SpellChecker
from nltk.tokenize import sent_tokenize
from spellchecker import SpellChecker
import language_tool_python
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import words
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip
import assemblyai as aai
import proglog
import tempfile
import requests
from nltk.tokenize import sent_tokenize
from spellchecker import SpellChecker
import language_tool_python
import re
from nltk.tokenize import sent_tokenize, word_tokenize

csv_file = "RedditClips\\movie_creation\\abbrevations.csv"
temp_files = []
known_acronyms = ["API", "HTML", "NASA"]
custom_words = ["temp"]  # Add any custom words here
spell = SpellChecker(language="en")
grammar_tool = language_tool_python.LanguageTool("en-US")


def set_temp(location):
    temp_files.append(location)


def get_temp():
    return temp_files


def add_missing_punctuation(sentence, prioritize_period=True):
    if not sentence.endswith((".", "!", "?")):
        sentence += "."

    if prioritize_period and sentence.endswith("."):
        sentence = sentence[:-1] + ","

    return sentence


def spell_check_word(word):
    params = {
        "text": word,
        "language": "en-US",
    }

    response = requests.post("https://languagetool.org/api/v2/check", params=params)
    if response.status_code == 200:
        result = response.json()
        if "matches" in result and result["matches"]:
            suggestions = [match["replacements"][0] for match in result["matches"]]
            return suggestions[0]
    return word


def bypass_known_acronyms(sentence):
    words = word_tokenize(sentence)

    for i in range(len(words)):
        if words[i].upper() in known_acronyms:
            words[i] = words[i].upper()

    return " ".join(words)


def load_abbreviations(csv_file):
    abbreviations = {}
    with open(csv_file, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                abbreviation, meaning = row
                abbreviations[abbreviation] = meaning
    return abbreviations


def replace_abbreviations(paragraph, abbreviations):
    words = paragraph.split()
    replaced_words = []

    for word in words:
        word = word.strip(".,!?()[]{}\"'")

        if word.upper() in abbreviations:
            replaced_words.append(abbreviations[word.upper()])
        else:
            replaced_words.append(word)

    modified_paragraph = " ".join(replaced_words)
    return modified_paragraph


def split_temp(text, max_length=200):
    segments = []
    current_segment = ""
    current_length = 0
    abbreviations = load_abbreviations(csv_file)
    text = replace_abbreviations(text, abbreviations)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    split_text = re.split(r"(?<=[,.])\s+", text)

    for segment in split_text:
        input_sentences = sent_tokenize(segment)

        for sentence in input_sentences:
            try:
                words = sentence.split()

                sentence = bypass_known_acronyms(sentence)

                corrected_words = []
                for word in words:
                    if word is not None:
                        if word in custom_words:
                            corrected_word = spell_check_word(word)
                            if corrected_word is None:
                                corrected_word = word
                        else:
                            corrected_word = spell.correction(word)
                            if corrected_word is None:
                                corrected_word = word
                        corrected_words.append(corrected_word)
                    else:
                        corrected_words.append(word)

                corrected_sentence = " ".join(corrected_words)

                corrected_sentence = add_missing_punctuation(
                    corrected_sentence, prioritize_period=True
                )

                if current_length + len(corrected_sentence) + 1 <= max_length:
                    if current_segment:
                        current_segment += " "
                    current_segment += corrected_sentence
                    current_length += len(corrected_sentence) + 1
                else:
                    segments.append(current_segment)
                    current_segment = corrected_sentence
                    current_length = len(corrected_sentence)

            except Exception as e:
                print(f"Error processing sentence: {e}")

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
    out_arr = []
    for segment in adjusted_segments:
        section_text = (
            f"{segment['start']/1000}~{segment['end']/1000}~{segment['text']}"
        )
        out_arr.append(section_text)
    return out_arr


def combine_audio_files(list):
    final_audio = AudioSegment.empty()
    for segment in list:
        audio_segment = AudioSegment.from_file(segment.filename, format="mp3")
        faded_audio = audio_segment.fade_out(200).fade_in(200)
        final_audio = final_audio + faded_audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_dir:
            temp_dir_path = temp_dir.name
            final_audio.export(temp_dir_path, format="wav")
        set_temp(temp_dir_path)
    audio_file_clip = AudioFileClip(temp_dir_path)

    return audio_file_clip


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


def set_title_start(video_path, audio, image_path, audio2):
    video = VideoFileClip(video_path)

    audio_final = concatenate_audioclips([audio, audio2])
    image_array = np.array(image_path)
    image_clip = ImageClip(image_array)

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


def add_captions(video_clip, audio_clip, output_video_path, transcriptions):
    text_clips = []

    font = "RedditClips\\title_image_data\\Stilu-Bold.otf"
    video_width, video_height = video_clip.size

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
            stroke_width=font_size * 0.05,
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
    print("Writing Video...")
    composite_video.write_videofile(
        output_video_path,
        threads=4,
        codec="nvenc_h264",
        fps=60,
        logger=proglog.TqdmProgressBarLogger(print_messages=False, leave_bars=True),
        ffmpeg_params=[
            "-threads",
            "4",
            "-movflags",
            "+faststart",
            "-c:v",
            "h264_nvenc",
            "-preset",
            "medium",
            "-tune",
            "animation",
            "-rc",
            "vbr",
            "-cq",
            "0",
            "-qmin:v",
            "10",
            "-qmax:v",
            "30",
            "-vf",
            "scale=1080:1920",
        ],
    )
    print("Video Uploaded to: {}".format(output_video_path))


def zoom_text(t, text_clip, zoom_factor, original_position):
    zoomed_clip = text_clip.resize(lambda t: 1 + zoom_factor * t)
    zoomed_clip = zoomed_clip.set_position(original_position)
    return zoomed_clip
