def generate_posters(event_name, organizer, venue, date, activities):
    os.makedirs('static/posters', exist_ok=True)

    font_path = "static/fonts/DejaVuLGCSerifCondensed-BoldItalic.ttf"
    path = "static/fonts/DejaVuLGCSerif-BoldItalic.ttf"
    font = "static/fonts/DejaVuLGCSerif.ttf"
    title_font = ImageFont.truetype(font_path, 80)
    content_font = ImageFont.truetype(path, 45)
    activity_font = ImageFont.truetype(font, 40)

    styles = [
        ("#fef3bd", "#0d0d0d", "#ff9800", "#4a148c"),
        ("#e0f7fa", "#006064", "#00acc1", "#1a237e"),
        ("#fce4ec", "#880e4f", "#d81b60", "#4a148c"),
        ("#e8f5e9", "#1b5e20", "#43a047", "#33691e"),
        ("#ede7f6", "#311b92", "#673ab7", "#4a148c"),
        ("#fff3e0", "#e65100", "#ff7043", "#bf360c"),
        ("#eceff1", "#263238", "#607d8b", "#37474f")
    ]

    for i, (bg_color, text_color, border_color, title_color) in enumerate(styles):
        img = Image.new("RGB", (800, 1000), bg_color)
        draw = ImageDraw.Draw(img)

        # Border
        draw.rectangle([0, 0, 799, 999], outline=border_color, width=10)

        # Title box
        title = event_name
        text_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = text_bbox[2] - text_bbox[0]
        title_height = text_bbox[3] - text_bbox[1]
        padding = 30
        box_x1, box_y1 = 50, 40
        box_x2 = box_x1 + title_width + padding * 2
        box_y2 = box_y1 + title_height + padding * 2

        # Draw title box
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill="lightgray", outline=title_color, width=4)
        draw.text((box_x1 + padding, box_y1 + padding), title, font=title_font, fill=title_color)

        # Info
        y = box_y2 + 40
        draw.text((50, y), f"ORGANIZER : {organizer}", font=content_font, fill=text_color); y += 60
        draw.text((50, y), f"VENUE : {venue}", font=content_font, fill=text_color); y += 60
        draw.text((50, y), f"DATE : {date}", font=content_font, fill=text_color); y += 80
        draw.text((50, y), "ACTIVITIES :", font=content_font, fill=text_color); y += 50

        for act in activities:
            draw.text((70, y), f"• {act['name']} – {act['time']}", font=activity_font, fill=text_color)
            y += 45

        # QR Code with proper line breaks
        activity_summary = "\n".join([f"{a['name']} at {a['time']}" for a in activities])
        qr_data = (
            f"Organizer Name : {organizer}\n" |
            f"Event Name : {event_name}\n" |
            f"Date : {date}\n" |
            f"Venue : {venue}\n" |
            f"Activities :\n{activity_summary}"
        )

        qr = qrcode.make(qr_data)
        qr = qr.resize((180, 180))
        img.paste(qr, (580, 780))

        filename = f"{event_name.replace(' ', '_')}_{i+1}.png"
        img.save(f"static/posters/{filename}")