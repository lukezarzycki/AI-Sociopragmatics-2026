import pandas as pd
import spacy
import matplotlib.pyplot as plt
import seaborn as sns

# Load the spaCy English model for dependency parsing
nlp = spacy.load("en_core_web_sm")

# Load the data (assuming the file is in the current directory)
df = pd.read_csv('modified_generated_data_with_analysis_new.csv')

# Function to extract dependency relations and count their frequency
def get_dependency_relation_count(text):
    doc = nlp(text)
    dep_rel_count = {}
    for token in doc:
        dep_rel = token.dep_
        if dep_rel not in dep_rel_count:
            dep_rel_count[dep_rel] = 1
        else:
            dep_rel_count[dep_rel] += 1
    return dep_rel_count

# Apply the function to each response to extract dependency relations
df_dep = df['AI Response'].apply(get_dependency_relation_count)

# Convert the results into a DataFrame
dep_df = pd.DataFrame(list(df_dep))

# Add the Tone column for grouping
dep_df['Tone'] = df['Tone']

# Group by Tone and sum the counts of each dependency relation
dep_by_tone = dep_df.groupby('Tone').sum()

# Print the results for inspection
print(dep_by_tone)

# Create a stacked bar chart to visualize the dependency relations by tone
plt.figure(figsize=(12, 8))
dep_by_tone.plot(kind='bar', stacked=True, colormap='coolwarm', figsize=(10, 7))
plt.title('Dependency Relation Counts by Tone')
plt.xlabel('Tone')
plt.ylabel('Count of Dependency Relations')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('dependency_relation_counts_by_tone.png')

# Show the plot
plt.show()