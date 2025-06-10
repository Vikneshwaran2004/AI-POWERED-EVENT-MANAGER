from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
import random

FONTS = ["arial.ttf", "arialbd.ttf"]  # Adjust based on your OS
COLORS = [
    ("#FFB6C1", "#000000"),
    ("#ADD8E6", "#000000"),
    ("#90EE90", "#000000"),
    ("#FFD700", "#000000")
]

def generate_qr_code(data, path):
    qr = qrcode.make(data)
    qr.save(path)

def generate_posters(event_name, organizer, date_time, venue, activities, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    qr_path = os.path.join(output_folder, "qr.png")
    generate_qr_code(f"{event_name} - {date_time}", qr_path)

    for i, (bg_color, text_color) in enumerate(COLORS):
        img = Image.new("RGB", (800, 1000), color=bg_color)
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype(FONTS[1], 50)
            font_normal = ImageFont.truetype(FONTS[0], 30)
        except:
            font_title = font_normal = ImageFont.load_default()

        y = 50
        draw.text((50, y), f"{event_name}", fill=text_color, font=font_title)
        y += 70
        draw.text((50, y), f"Organizer: {organizer}", fill=text_color, font=font_normal)
        y += 40
        draw.text((50, y), f"Date & Time: {date_time}", fill=text_color, font=font_normal)
        y += 40
        draw.text((50, y), f"Venue: {venue}", fill=text_color, font=font_normal)
        y += 60
        draw.text((50, y), "Activities:", fill=text_color, font=font_normal)
        for act in activities:
            y += 35
            draw.text((70, y), f"• {act}", fill=text_color, font=font_normal)

        qr_img = Image.open(qr_path).resize((180, 180))
        img.paste(qr_img, (600, 800))

        img.save(os.path.join(output_folder, f"poster_{i+1}.png"))
