import pandas as pd

# Załaduj dane z lokalnego pliku CSV
df = pd.read_csv('modified_generated_data_with_analysis_new.csv')

# Oblicz średnią liczbę słów w odpowiedzi w zależności od tonu
word_count_by_tone = df.groupby('Tone')['word_count'].mean()

# Wyświetl wyniki
print("Detailed Word Count by Tone:")
print(word_count_by_tone)