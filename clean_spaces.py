file_path = "app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace non-breaking spaces with regular space
cleaned = content.replace('\u00A0', ' ')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Fixed non-breaking spaces.")
