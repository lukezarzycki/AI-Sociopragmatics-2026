import pandas as pd

# Załaduj dane z pliku CSV
df_analysis = pd.read_csv('generated_data_with_analysis.csv')

# Oblicz średni sentyment w zależności od tonu
sentiment_by_tone = df_analysis.groupby('Tone')['sentiment'].mean()

# Oblicz średnią liczbę słów w odpowiedzi w zależności od tonu
word_count_by_tone = df_analysis.groupby('Tone')['word_count'].mean()

# Wyświetl wyniki
print("Average Sentiment by Tone:")
print(sentiment_by_tone)

print("\nAverage Word Count by Tone:")
print(word_count_by_tone)

# Zapisz dane do nowego pliku CSV
df_analysis.to_csv('modified_generated_data_with_analysis.csv', index=False)
print('Plik CSV z wynikami zapisano jako modified_generated_data_with_analysis.csv')