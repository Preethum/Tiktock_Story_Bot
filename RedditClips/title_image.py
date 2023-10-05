from PIL import Image, ImageDraw, ImageFont
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
import textwrap


font = ""


def add_corners(im):
    rad = 50
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def add_title(image, text):
    width, height = image.size
    font_color = (255, 255, 255)
    font_path = "RedditClips\\title_image_data\\NeueHaasDisplayMediu.ttf"

    draw = ImageDraw.Draw(image)

    textbox_x = 50
    textbox_y = 260
    textbox_width = width - 100
    textbox_height = height - 400

    max_font_size = 130

    for font_size in range(max_font_size, 0, -1):
        font = ImageFont.truetype(font_path, font_size)

        lines = []
        current_line = ""
        for word in text.split():
            test_line = current_line + word + " "
            test_width, _ = draw.textsize(test_line, font=font)
            if test_width <= (textbox_width - 20):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        text_height = sum(font.getsize(line)[1] for line in lines)

        if text_height <= textbox_height:
            best_font_size = font_size
            best_text_lines = lines
            best_text_height = text_height
            break

    text_x = textbox_x
    text_y = textbox_y

    draw.text(
        (310, 40), "Anonymous", fill=(0, 0, 0), font=ImageFont.truetype(font_path, 80)
    )
    draw.text(
        (423, 701),
        "99+",
        fill=(128, 128, 128),
        font=ImageFont.truetype(
            "RedditClips\\title_image_data\\NeueHaasDisplayRoman.ttf", 60
        ),
    )
    draw.text(
        (130, 701),
        "99+",
        fill=(128, 128, 128),
        font=ImageFont.truetype(
            "RedditClips\\title_image_data\\NeueHaasDisplayRoman.ttf", 60
        ),
    )

    lines = []
    current_line = ""
    for word in text.split():
        test_line = current_line + word + " "
        test_width, _ = draw.textsize(test_line, font=font)
        if test_width <= (textbox_width - 20):
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for line in lines:
        draw.text((text_x, text_y), line, fill=(0, 0, 0), font=font)
        text_y += font.getsize(line)[1]

    return image
