import pandas as pd

# Załaduj dane z pliku CSV
df = pd.read_csv('generated_data.csv')  # lub pełna ścieżka do pliku

# Sprawdźmy pierwsze kilka wierszy danych
print(df.head())