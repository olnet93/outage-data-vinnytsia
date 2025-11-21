import os
import json
from PIL import Image, ImageDraw, ImageFont

# 1. Створюємо папку для картинок
os.makedirs("images/vinnytsia", exist_ok=True)

# 2. Читаємо JSON з графіками
with open("data/vinnytsia.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. Розміри зображення
WIDTH_PER_HOUR = 25
HEIGHT = 100
MARGIN = 20

# 4. Шрифти (якщо немає шрифту — PIL використає стандартний)
try:
    FONT = ImageFont.truetype("arial.ttf", 14)
except:
    FONT = ImageFont.load_default()

# 5. Генеруємо картинки для кожної черги
for queue in data.get("queues", []):
    hours = queue.get("hours", [])
    img_width = WIDTH_PER_HOUR * len(hours) + MARGIN*2
    img = Image.new("RGB", (img_width, HEIGHT + MARGIN*2), color="white")
    draw = ImageDraw.Draw(img)

    # 6. Малюємо прямокутники для годин
    for i, hour in enumerate(hours):
        x0 = MARGIN + i * WIDTH_PER_HOUR
        y0 = MARGIN
        x1 = x0 + WIDTH_PER_HOUR - 1
        y1 = y0 + HEIGHT

        # Білий або червоний
        if hour.get("disconnection"):
            color = (255, 0, 0)  # червоний
        else:
            color = (255, 255, 255)  # білий

        # Сірий фон для непарних годин
        if i % 2 == 1:
            base = Image.new("RGB", (WIDTH_PER_HOUR, HEIGHT), (230, 230, 230))
            img.paste(base, (x0, y0))

        draw.rectangle([x0, y0, x1, y1], fill=color, outline="black")

        # Підпис години
        draw.text((x0 + 3, y1 - 18), str(i), fill="black", font=FONT)

    # 7. Назва черги
    draw.text((MARGIN, 2), queue.get("name", ""), fill="black", font=FONT)

    # 8. Зберігаємо картинку
    filename = f"images/vinnytsia/{queue.get('name','queue')}.png"
    img.save(filename)
    print(f"{filename} згенеровано!")

print("Всі картинки згенеровані ✅")
