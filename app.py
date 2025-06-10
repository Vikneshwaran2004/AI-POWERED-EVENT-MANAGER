from flask import Flask, render_template, request, redirect, send_file, url_for
from fpdf import FPDF
import os
import json
from PIL import Image, ImageDraw, ImageFont
import qrcode
from datetime import datetime
from itertools import cycle

app = Flask(__name__)
SCHEDULE_FILE = 'schedules.json'

# Load existing schedules
def load_schedules():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return []

# Save updated schedules
def save_schedules(schedules):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedules, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event = {
            'event_name': request.form['event_name'],
            'organizer': request.form['organizer'],
            'venue': request.form['venue'],
            'date': request.form['date'],
            'activities': []
        }

        activities_raw = request.form['activities'].strip().split('\n')
        base_time = datetime.strptime("10:00", "%H:%M")

        for i, activity in enumerate(activities_raw):
            time_str = (base_time.replace(minute=(base_time.minute + i*60) % 60, hour=(base_time.hour + i))) \
                .strftime("%I:%M %p")
            event['activities'].append({'name': activity.strip(), 'time': time_str})

        schedules = load_schedules()
        schedules.append(event)
        save_schedules(schedules)

        # 🧠 Generate poster for event
        generate_posters(event['event_name'], event['organizer'], event['venue'], event['date'], event['activities'])

        return redirect(url_for('view_schedules'))
    return render_template('create.html')

@app.route('/schedules')
def view_schedules():
    schedules = load_schedules()
    return render_template('schedules.html', schedules=schedules)

@app.route('/history')
def history():
    schedules = load_schedules()
    return render_template('history.html', schedules=schedules)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    index = int(request.form['index'])
    updated_activities = request.form.getlist('activity[]')
    updated_times = request.form.getlist('time[]')

    schedules = load_schedules()
    new_activity_list = []

    for name, time in zip(updated_activities, updated_times):
        new_activity_list.append({'name': name, 'time': time})

    schedules[index]['activities'] = new_activity_list
    save_schedules(schedules)
    return redirect(url_for('view_schedules'))

@app.route('/download_schedule/<int:index>')
def download_schedule(index):
    schedules = load_schedules()
    event = schedules[index]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Schedule for {event['event_name']}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Organizer: {event['organizer']}", ln=True)
    pdf.cell(200, 10, txt=f"Venue: {event['venue']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {event['date']}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Activities:", ln=True)

    for act in event['activities']:
        pdf.cell(200, 10, txt=f"{act['name']} - {act['time']}", ln=True)

    filename = f"{event['event_name'].replace(' ', '_')}_schedule.pdf"
    filepath = os.path.join("static", filename)
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

@app.route('/poster_archive')
def poster_archive():
    posters = os.listdir('static/posters')
    return render_template('poster_archive.html', posters=posters)

import os
from PIL import Image, ImageDraw, ImageFont
import qrcode

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import qrcode
from itertools import cycle

def generate_posters(event_name, organizer, venue, date, activities):
    os.makedirs('static/posters', exist_ok=True)

    title_font = ImageFont.truetype("static/fonts/MetalMania-Regular.ttf", 75)
    content_font = ImageFont.truetype("static/fonts/Rye-Regular.ttf", 45)
    activity_font = ImageFont.truetype("static/fonts/Merienda-VariableFont_wght.ttf", 40)

    styles = [
        ("#fffdf5", "#1a1a1a", "#4a90e2", "#d32f2f"),
        ("#f0f4c3", "#263238", "#4caf50", "#1b5e20"),
        ("#e0f7fa", "#006064", "#00acc1", "#1a237e"),
        ("#fce4ec", "#880e4f", "#d81b60", "#4a148c"),
        ("#ede7f6", "#311b92", "#673ab7", "#4a148c")
    ]
    style_cycle = cycle(styles)

    for i in range(10):
        logo_path = f"static/logos/logo{i+1}.png"
        logo = Image.open(logo_path).convert("RGBA").resize((130, 130)) if os.path.exists(logo_path) else None

        if i < 5:
            bg_path = f"static/backgrounds/bg{i+1}.jpg"
            img = Image.open(bg_path).resize((800, 1000)).convert("RGB")
            draw = ImageDraw.Draw(img)
            text_color = "#000000"
            title_color = "#000000"
        else:
            bg_color, text_color, border_color, title_color = next(style_cycle)
            img = Image.new("RGB", (800, 1000), bg_color)
            draw = ImageDraw.Draw(img)
            draw.rectangle([0, 0, 799, 999], outline=border_color, width=10)

        # Logo
        if logo:
            img.paste(logo, (335, 20), logo)

        # Title box with center alignment
        title_text = event_name.upper()
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = bbox[2] - bbox[0]
        title_h = bbox[3] - bbox[1]
        title_x = (800 - title_w) // 2
        title_y = 170
        draw.rectangle(
            [title_x - 30, title_y - 20, title_x + title_w + 30, title_y + title_h + 20],
            fill="white", outline=title_color, width=4
        )
        draw.text((title_x, title_y), title_text, font=title_font, fill=title_color)

        # Transparent box behind text section (for visibility)
        text_bg = Image.new("RGBA", (700, 600), (255, 255, 255, 180))  # white with alpha
        img.paste(text_bg, (50, 270), text_bg)
        draw = ImageDraw.Draw(img)

        # Text content
        y = 290
        draw.text((60, y), f"Organizer : {organizer}", font=content_font, fill=text_color); y += 55
        draw.text((60, y), f"Venue     : {venue}", font=content_font, fill=text_color); y += 55
        draw.text((60, y), f"Date      : {date}", font=content_font, fill=text_color); y += 70
        draw.text((60, y), "Activities:", font=content_font, fill=text_color); y += 50

        for act in activities:
            draw.text((80, y), f"• {act['name']} – {act['time']}", font=activity_font, fill=text_color)
            y += 42

        # QR Code
        activity_list = "\n".join([f"{a['name']} at {a['time']}" for a in activities])
        qr_data = (
            f"Organizer Name : {organizer}\n"
            f"Event Name     : {event_name}\n"
            f"Date           : {date}\n"
            f"Venue          : {venue}\n"
            f"Activities     :\n{activity_list}"
        )
        qr = qrcode.make(qr_data).resize((180, 180))
        img.paste(qr, (600, 780))

        # Save file
        filename = f"{event_name.replace(' ', '_')}_{i+1}.png"
        img.save(f"static/posters/{filename}")



if __name__ == '__main__':
    app.run(debug=True)
