import pandas as pd
import spacy
import matplotlib.pyplot as plt
import seaborn as sns

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Load the data
df = pd.read_csv('modified_generated_data_with_analysis_new.csv')

# Function to extract POS counts for a given text
def get_pos_count(text):
    doc = nlp(text)
    pos_count = {
        "NOUN": 0,
        "VERB": 0,
        "ADJ": 0,
        "ADV": 0,
        "PRON": 0,
        "DET": 0,
        "ADP": 0,
        "CONJ": 0,
        "INTJ": 0,
        "PUNCT": 0,
        "SYM": 0,
        "X": 0
    }
    
    for token in doc:
        if token.pos_ in pos_count:
            pos_count[token.pos_] += 1
    
    return pos_count

# Apply POS tagging function to each AI response and store the results in a new column
df_pos = df['AI Response'].apply(get_pos_count)

# Convert the results into a DataFrame
pos_df = pd.DataFrame(list(df_pos))

# Add the Tone column for grouping
pos_df['Tone'] = df['Tone']

# Group by Tone and sum the POS counts
pos_by_tone = pos_df.groupby('Tone').sum()

# Print the result for inspection
print(pos_by_tone)

# Visualization using Seaborn
plt.figure(figsize=(12, 8))
pos_by_tone.plot(kind='bar', stacked=True, colormap='Blues', figsize=(10, 7))
plt.title('Part of Speech (POS) Counts by Tone')
plt.xlabel('Tone')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
plt.savefig('POS_counts_by_tone.png')

# Show the plot
plt.show()