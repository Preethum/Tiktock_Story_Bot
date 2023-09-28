import Reddit
import tiktockvoice.tiktokvoice
import title_image
import movie_creation.movie_creator as movie
from PIL import Image
import re
import os, shutil
import random
import argparse
import configparser

parser = argparse.ArgumentParser(
    description="A script that makes a video from link if no link will pull the top post"
)
parser.add_argument("-l", "--variable_a", type=str, default=None, help="Pull Link")
args = parser.parse_args()
variable_a = args.variable_a


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
if variable_a is not None:
    reddit_link.append(variable_a)
else:
    reddit_link = Reddit.find_top_posts(reddit_data, "stories", 1)


def sanitize_filename(filename):
    disallowed_chars = r'[\/:*?"<>|]'

    sanitized_filename = re.sub(disallowed_chars, "", filename)

    return sanitized_filename


for url in reddit_link:
    post_data_dict = {}
    post_data = Reddit.fetch_reddit_post_data(url, reddit_data)
    for key, value in post_data.items():
        if key == "Title":
            value = sanitize_filename(value)
        post_data_dict[key] = value

    image_path = r"title_image_data\\Reddit_card.png"
    image = Image.open(image_path)
    image = title_image.add_corners(image)
    image = title_image.add_title(image, post_data_dict["Title"])
    image.save("cache\\curr_title_img.png")

    segaments = movie.split_temp(post_data_dict["Text"], max_length=200)

    file_list = []
    seg_number = 0
    voice = [
        "en_au_002",
        "en_au_001",
        "en_us_001",
        "en_us_002",
        "en_us_006",
        "en_us_007",
        "en_us_ghostface",
        "en_us_c3po",
        "en_us_010",
    ]
    voice_user = random.choice(voice)
    for segament in segaments:
        tiktockvoice.tiktokvoice.tts(
            segament, voice_user, "cache\\Story_output{}.mp3".format(seg_number)
        )
        file_list.append("cache\\Story_output{}.mp3".format(seg_number))

        seg_number = seg_number + 1

    movie.combine_audio_files(file_list)

    tiktockvoice.tiktokvoice.tts(
        post_data_dict["Title"], voice_user, "cache\\Title_output.mp3"
    )

    movie.convert_to_wav("cache\\Story_output.mp3", "cache\\Story_output.wav")
    result_string = re.sub(r"\n", "", post_data_dict["Text"])

    result_string = result_string.replace("\n", " ")
    config = configparser.ConfigParser()
    config_file = "config.txt"
    config.read(config_file)
    if config.has_section("ASSEMBLYAI"):
        client_id = config.get("ASSEMBLYAI", "key")
        movie.captions("cache\\Story_output.wav", client_id)

    vid_name = "background_vids//vid_1.mp4"
    if os.path.isdir("background_vids"):
        files = os.listdir("background_vids")

        files = [f for f in files if os.path.isfile(os.path.join("background_vids", f))]

        if len(files) > 0:
            random_file = random.choice(files)

            vid_name = "background_vids//{}".format(random_file)
        else:
            print("The folder is empty.")
    else:
        print("The specified path is not a directory.")

    final_clip = movie.set_title_start(
        vid_name,
        "cache\\Title_output.mp3",
        "cache\\curr_title_img.png",
        "cache\\Story_output.wav",
    )
    movie.add_captions(
        final_clip,
        "cache\\Title_output.mp3",
        "output_video\\{}.mp4".format(post_data_dict["Title"]),
    )

    folder = "cache"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))
