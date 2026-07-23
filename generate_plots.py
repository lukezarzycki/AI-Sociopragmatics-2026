import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

# Załaduj dane z lokalnego pliku CSV
df = pd.read_csv('modified_generated_data_with_analysis_new.csv')  # Zaktualizowana ścieżka do pliku

# Funkcja do analizy sentymentu
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Funkcja do liczenia liczby słów w odpowiedzi
def word_count(text):
    return len(text.split())

# Oblicz sentyment tylko wtedy, gdy kolumna 'sentiment' nie istnieje
if 'sentiment' not in df.columns:
    df['sentiment'] = df['AI Response'].apply(analyze_sentiment)

# Dodaj kolumnę 'word_count' do danych
df['word_count'] = df['AI Response'].apply(word_count)

# Oblicz średni sentyment w zależności od tonu
sentiment_by_tone = df.groupby('Tone')['sentiment'].mean()

# Oblicz średnią liczbę słów w odpowiedzi w zależności od tonu
word_count_by_tone = df.groupby('Tone')['word_count'].mean()

# Wyświetl wyniki
print("Average Sentiment by Tone:")
print(sentiment_by_tone)

print("\nAverage Word Count by Tone:")
print(word_count_by_tone)

# Tworzenie wykresów

# Wykres 1: Średni sentyment odpowiedzi AI w zależności od tonu
plt.figure(figsize=(8, 6))
sns.barplot(x=sentiment_by_tone.index, y=sentiment_by_tone.values, palette='coolwarm')
plt.title('Average Sentiment of AI Responses by Tone')
plt.xlabel('Tone')
plt.ylabel('Average Sentiment')
plt.tight_layout()

# Zapisz wykres jako plik PNG
plt.savefig('average_sentiment_by_tone.png')
plt.close()  # Zamknij wykres, aby zapisać go do pliku

# Wykres 2: Średnia liczba słów w odpowiedzi AI w zależności od tonu
plt.figure(figsize=(8, 6))
sns.barplot(x=word_count_by_tone.index, y=word_count_by_tone.values, palette='Blues')
plt.title('Average Word Count of AI Responses by Tone')
plt.xlabel('Tone')
plt.ylabel('Average Word Count')
plt.tight_layout()

# Zapisz wykres jako plik PNG
plt.savefig('average_word_count_by_tone.png')
plt.close()  # Zamknij wykres

# Zapisz dane do nowego pliku CSV
df.to_csv('modified_generated_data_with_analysis_new.csv', index=False)
print('CSV file with results saved as modified_generated_data_with_analysis_new.csv')

# Sprawdź, gdzie zapisano wykresy
print("Wykresy zapisane w lokalnym folderze jako:")
print("- average_sentiment_by_tone.png")
print("- average_word_count_by_tone.png")