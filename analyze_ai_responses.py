import pandas as pd
from textblob import TextBlob

# Załaduj dane z pliku CSV
df = pd.read_csv('generated_data.csv')

# Sprawdzamy, jakie kolumny znajdują się w pliku
print(df.columns)

# Analizujemy próbkę danych, żeby zobaczyć, co się dzieje
print(df.head())

# Funkcja do analizy sentymentu
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Obliczamy sentyment dla każdej odpowiedzi
df['sentiment'] = df['AI Response'].apply(analyze_sentiment)

# Sprawdzamy, jak wygląda rozkład sentymentu
print(df[['Tone', 'sentiment']].groupby('Tone').mean())

# Liczymy liczbę słów w odpowiedzi
df['word_count'] = df['AI Response'].apply(lambda x: len(x.split()))

# Sprawdzamy średnią liczbę słów w odpowiedzi dla każdego tonu
print(df[['Tone', 'word_count']].groupby('Tone').mean())

# Zapisz dane do nowego pliku CSV
output_file = 'generated_data_with_analysis.csv'
df.to_csv(output_file, index=False)
print(f'Plik CSV z analizami zapisano jako {output_file}')