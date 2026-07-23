import pandas as pd

# Załaduj dane z lokalnego pliku CSV
df = pd.read_csv('modified_generated_data_with_analysis_new.csv')

# Oblicz średni sentyment w zależności od tonu
sentiment_by_tone = df.groupby('Tone')['sentiment'].mean()

# Oblicz średnią liczbę słów w odpowiedzi w zależności od tonu
word_count_by_tone = df.groupby('Tone')['word_count'].mean()

# Wyświetl wyniki dokładnie
print("Detailed Sentiment by Tone:")
print(sentiment_by_tone)

print("\nDetailed Word Count by Tone:")
print(word_count_by_tone)