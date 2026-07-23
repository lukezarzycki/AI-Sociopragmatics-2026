from PIL import Image

# Załaduj plik PNG
image_path = 'average_sentiment_by_tone.png'  # Zmień na ścieżkę do swojego pliku
img = Image.open(image_path)

# Wymiary obrazu
width, height = img.size

# Podziel obraz na dwie części
left_part = img.crop((0, 0, width // 2, height))  # Lewa połowa
right_part = img.crop((width // 2, 0, width, height))  # Prawa połowa

# Zapisz dwie części jako osobne pliki PNG
left_part.save('left_average_sentiment_by_tone.png')
right_part.save('right_average_sentiment_by_tone.png')

print("Wykresy zostały zapisane jako 'left_average_sentiment_by_tone.png' oraz 'right_average_sentiment_by_tone.png'")