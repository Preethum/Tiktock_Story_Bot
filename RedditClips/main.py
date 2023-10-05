import Reddit as Reddit
import tiktockvoice.tiktokvoice
import title_image
import movie_creation.movie_creator as movie
from PIL import Image
import re
from moviepy.audio.fx.volumex import volumex
import os, shutil
import random
import argparse
import configparser
import tempfile
from moviepy.editor import *
import proglog
import time

parser = argparse.ArgumentParser(
    description="A script that makes a video from link if no link will pull the top post"
)
parser.add_argument("-l", "--variable_a", type=str, default=None, help="Pull Link")
parser.add_argument("-t", "--variable_b", type=str, default=None, help="Title")
parser.add_argument("-s", "--variable_c", type=str, default=None, help="Story")
args = parser.parse_args()
variable_a = args.variable_a
variable_b = args.variable_b
variable_c = args.variable_c
temp_file_dir = []

print(
    """

 _______                   __        __  __    __             ______    __                                             
/       \                 /  |      /  |/  |  /  |           /      \  /  |                                            
$$$$$$$  |  ______    ____$$ |  ____$$ |$$/  _$$ |_         /$$$$$$  |_$$ |_     ______    ______   __    __   _______ 
$$ |__$$ | /      \  /    $$ | /    $$ |/  |/ $$   |        $$ \__$$// $$   |   /      \  /      \ /  |  /  | /       |
$$    $$< /$$$$$$  |/$$$$$$$ |/$$$$$$$ |$$ |$$$$$$/         $$      \$$$$$$/   /$$$$$$  |/$$$$$$  |$$ |  $$ |/$$$$$$$/ 
$$$$$$$  |$$    $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ | __        $$$$$$  | $$ | __ $$ |  $$ |$$ |  $$/ $$ |  $$ |$$      \ 
$$ |  $$ |$$$$$$$$/ $$ \__$$ |$$ \__$$ |$$ |  $$ |/  |      /  \__$$ | $$ |/  |$$ \__$$ |$$ |      $$ \__$$ | $$$$$$  |
$$ |  $$ |$$       |$$    $$ |$$    $$ |$$ |  $$  $$/       $$    $$/  $$  $$/ $$    $$/ $$ |      $$    $$ |/     $$/ 
$$/   $$/  $$$$$$$/  $$$$$$$/  $$$$$$$/ $$/    $$$$/         $$$$$$/    $$$$/   $$$$$$/  $$/        $$$$$$$ |$$$$$$$/  
                                                                                                   /  \__$$ |          
                                                                                                   $$    $$/           
                                                                                                    $$$$$$/"""
)


reddit = ""
config = ""
reddit_link = []
reddit_data = Reddit.set_up_config_settings()


def sanitize_filename(filename):
    disallowed_chars = r'[\/:*?"<>|]'

    sanitized_filename = re.sub(disallowed_chars, "", filename)

    return sanitized_filename


def sanitize_string(input_string):
    pattern = re.compile("[^\x00-\x7F]+")
    sanitized_string = pattern.sub("", input_string)
    return sanitized_string


def make_video(title, text):
    title = sanitize_string(sanitize_filename(title))
    text = sanitize_string(text)
    image_path = r"RedditClips\\title_image_data\\Reddit_card.png"
    image = Image.open(image_path)
    image = title_image.add_corners(image)
    print("Generating Title Card...")
    image = title_image.add_title(image, title)
    segaments = movie.split_temp(text, max_length=200)

    file_list = []

    voice = [
        "en_au_002",
        "en_au_001",
        "en_us_001",
        "en_us_002",
        "en_us_006",
        "en_us_007",
        "en_us_ghostface",
        "en_us_010",
    ]
    voice_user = random.choice(voice)

    for segament in segaments:
        audio_clip = tiktockvoice.tiktokvoice.tts(segament, voice_user, True)
        file_list.append(audio_clip)
    story_mp3 = movie.combine_audio_files(file_list)
    speed_factor = 1.2
    ffmpeg_params = ["-af", f"atempo={speed_factor}"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        print("Writing Audio...")
        temp_audio_path = temp_audio_file.name
        story_mp3.write_audiofile(
            temp_audio_path,
            codec="pcm_s16le",
            ffmpeg_params=ffmpeg_params,
            logger=proglog.TqdmProgressBarLogger(
                print_messages=False, leave_bars=True, ignore_bars_under=True
            ),
        )

    tiktockvoice.tiktokvoice.set_temp(temp_audio_path)

    title_mp3 = tiktockvoice.tiktokvoice.tts(title, voice_user, False)

    result_string = re.sub(r"\n", "", text)

    result_string = result_string.replace("\n", " ")
    config = configparser.ConfigParser()
    config_file = "RedditClips\\config.txt"
    config.read(config_file)
    transcript = []
    if config.has_section("ASSEMBLYAI"):
        client_id = config.get("ASSEMBLYAI", "key")

        transcript = movie.captions(temp_audio_path, client_id)

    vid_name = ""
    if os.path.isdir("RedditClips//background_vids"):
        files = os.listdir("RedditClips//background_vids")

        files = [
            f
            for f in files
            if os.path.isfile(os.path.join("RedditClips//background_vids", f))
        ]

        if len(files) > 0:
            random_file = random.choice(files)

            vid_name = "RedditClips//background_vids//{}".format(random_file)
        else:
            print("The folder is empty.")
    else:
        print("The specified path is not a directory.")

    final_clip = movie.set_title_start(
        vid_name,
        title_mp3,
        image,
        AudioFileClip(temp_audio_path),
    )
    movie.add_captions(
        final_clip,
        title_mp3,
        "RedditClips\\output_video\\{}.mp4".format(title),
        transcript,
    )
    time.sleep(5)
    for file_to_delete in tiktockvoice.tiktokvoice.get_temp():
        file = open(file_to_delete, "r")
        file.close()
        try:
            os.remove(file_to_delete)
        except FileNotFoundError:
            print(f"File '{file_to_delete}' not found.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {str(e)}")
    for file_to_delete in movie.get_temp():
        file = open(file_to_delete, "r")
        file.close()
        try:
            os.remove(file_to_delete)
        except FileNotFoundError:
            print(f"File '{file_to_delete}' not found.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {str(e)}")


if variable_a is not None:
    post_data_dict = {}
    post_data = Reddit.fetch_reddit_post_data(variable_a, reddit_data)
    for key, value in post_data.items():
        if key == "Title":
            value = sanitize_filename(value)
        post_data_dict[key] = value
    print(post_data_dict["Title"])
    print(post_data_dict["Text"])
    make_video(post_data_dict["Title"], post_data_dict["Text"])
elif variable_b is not None and variable_c is not None:
    make_video(variable_b, variable_c)
else:
    print("Error has occured...")
