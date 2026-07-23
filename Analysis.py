import os
from dotenv import load_dotenv
from openai import OpenAI

# Ta linijka szuka pliku .env na Twoim komputerze i pobiera z niego klucz
load_dotenv()

# Inicjalizacja klienta OpenAI za pomocą bezpiecznej zmiennej
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Przykład testowego zapytania do modelu:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)