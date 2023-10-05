import threading, requests, base64
from playsound import playsound
from moviepy.editor import AudioFileClip
import tempfile


temp_files = []


def set_temp(location):
    temp_files.append(location)


def get_temp():
    return temp_files


VOICES = [
    "en_us_ghostface",
    "en_us_chewbacca",
    "en_us_c3po",
    "en_us_stitch",
    "en_us_stormtrooper",
    "en_us_rocket",
    "en_au_001",
    "en_au_002",
    "en_uk_001",
    "en_uk_003",
    "en_us_001",
    "en_us_002",
    "en_us_006",
    "en_us_007",
    "en_us_009",
    "en_us_010",
    "fr_001",
    "fr_002",
    "de_001",
    "de_002",
    "es_002",
    "es_mx_002",
    "br_001",
    "br_003",
    "br_004",
    "br_005",
    "id_001",
    "jp_001",
    "jp_003",
    "jp_005",
    "jp_006",
    "kr_002",
    "kr_003",
    "kr_004",
    "en_female_f08_salut_damour",
    "en_male_m03_lobby",
    "en_female_f08_warmy_breeze",
    "en_male_m03_sunshine_soon",
    "en_male_narration",
    "en_male_funny",
    "en_female_emotional",
]

ENDPOINTS = [
    "https://tiktok-tts.weilnet.workers.dev/api/generation",
    "https://tiktoktts.com/api/tiktok-tts",
]
current_endpoint = 0

TEXT_BYTE_LIMIT = 300


def split_string(string: str, chunk_size: int) -> list[str]:
    words = string.split()
    result = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:
            current_chunk += " " + word
        else:
            if current_chunk:
                result.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:
        result.append(current_chunk.strip())
    return result


def get_api_response() -> requests.Response:
    url = f'{ENDPOINTS[current_endpoint].split("/a")[0]}'
    response = requests.get(url)
    return response


def save_audio_file(base64_data: str, Title: False):
    audio_bytes = base64.b64decode(base64_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio_bytes)

    temp_audio_path = temp_audio_file.name
    set_temp(temp_audio_path)

    audio_clip = AudioFileClip(temp_audio_path)
    if Title is True:
        audio_clip = audio_clip.subclip(0.4, -0.4)

    return audio_clip


def generate_audio(text: str, voice: str) -> bytes:
    url = f"{ENDPOINTS[current_endpoint]}"
    headers = {"Content-Type": "application/json"}
    data = {"text": text, "voice": voice}
    response = requests.post(url, headers=headers, json=data)
    return response.content


def tts(text: str, voice: str = "none", Title=False):
    global current_endpoint
    if get_api_response().status_code != 200:
        current_endpoint = (current_endpoint + 1) % 2
        if get_api_response().status_code != 200:
            print(
                f"Service not available and probably temporarily rate limited, try again later..."
            )
            return

    if voice == "none":
        print("No voice has been selected")
        return

    if not voice in VOICES:
        print("Voice does not exist")
        return

    if len(text) == 0:
        print("Insert a valid text")
        return

    try:
        if len(text) < TEXT_BYTE_LIMIT:
            audio = generate_audio((text), voice)
            if current_endpoint == 0:
                audio_base64_data = str(audio).split('"')[5]
            else:
                audio_base64_data = str(audio).split('"')[3].split(",")[1]

            if audio_base64_data == "error":
                print("This voice is unavailable right now")
                return

        else:
            text_parts = split_string(text, 299)
            audio_base64_data = [None] * len(text_parts)

            def generate_audio_thread(text_part, index):
                audio = generate_audio(text_part, voice)
                if current_endpoint == 0:
                    base64_data = str(audio).split('"')[5]
                else:
                    base64_data = str(audio).split('"')[3].split(",")[1]

                if audio_base64_data == "error":
                    print("This voice is unavailable right now")
                    return "error"

                audio_base64_data[index] = base64_data

            threads = []
            for index, text_part in enumerate(text_parts):
                thread = threading.Thread(
                    target=generate_audio_thread, args=(text_part, index)
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            audio_base64_data = "".join(audio_base64_data)

        audio_clip = save_audio_file(audio_base64_data, Title)

        return audio_clip

    except Exception as e:
        print("Error occurred while generating audio:", str(e))
