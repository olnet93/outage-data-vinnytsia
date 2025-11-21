import os
import json
from PIL import Image, ImageDraw

# 1. Створюємо папку для картинок
os.makedirs("images/vinnytsia", exist_ok=True)

# 2. Читаємо JSON з графіками
with open("data/vinnytsia.json") as f:
    data = json.load(f)

# 3. Генеруємо картинки (по одній на чергу)
for queue in data["queues"]:
    img = Image.new("RGB", (600, 100), color="white")
    draw = ImageDraw.Draw(img)
    
    # приклад: малюємо прямокутники по годинах
    for i, hour in enumerate(queue["hours"]):
        color = "red" if hour["disconnection"] else "white"
        draw.rectangle([i*20, 0, i*20+20, 100], fill=color)
    
    # 4. Зберігаємо картинку
    img.save(f"images/vinnytsia/{queue['name']}.png")

print("Images generated!")
