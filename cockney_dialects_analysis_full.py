# cockney_dialects_analysis_full.py

import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer, util

# -----------------------------
# 1️⃣ Definicje dialektów i 50 fraz
# -----------------------------
dialekty = {
    "Cockney": [
        "apples", "butchers", "dog", "Rosie", "trouble", "plates", "whistle",
        "jam", "china", "loaf", "dustbin", "ruby", "loafers", "bottle", "tea",
        "barnet", "pony", "nipper", "chinwag", "sparrow", "applesauce", "troublemaker",
        "peckham", "brass", "ginger", "baker", "jammy", "fiddle", "sarnie", "rabbit",
        "mince", "nanny", "boots", "tray", "ponytail", "lilly", "robin", "sugar",
        "cork", "biscuit", "cider", "milk", "jammydodger", "applepie", "butcherhook",
        "battle", "lemon", "whistleflute", "cherry", "bowler"
    ],
    "Brummie": [
        "bab", "ginnel", "bostin", "owt", "nowt", "chuddy", "nana", "snap", "mardy",
        "bostinly", "scran", "laff", "twit", "snob", "gob", "knackered", "lolly",
        "lump", "jammy", "natter", "scrumpy", "barmy", "blinder", "toss", "lolly", "scran",
        "bostin", "ginnel", "owt", "nowt", "snap", "twit", "mardy", "bab", "lump", "nana",
        "blinder", "scrumpy", "gob", "barmy", "toss", "laff", "jammy", "twit", "natter", "scran", "lolly"
    ],
    "Scouse": [
        "la", "boss", "scally", "sound", "la-dee", "bizzy", "bevvy", "cob", "giz", "ta",
        "laddo", "la-la", "gob", "cobblers", "scran", "spice", "jing", "slag", "lush", "natter",
        "bossy", "scouse", "gannin", "hinny", "lummox", "mate", "youse", "boss", "la", "spice",
        "scran", "jing", "giz", "cob", "ta", "bevvy", "la-dee", "bizzy", "natter", "lush",
        "gob", "mate", "youse", "hinny", "laddo", "scally", "bossy", "la-la", "gannin", "spice"
    ],
    "Geordie": [
        "canny", "hinny", "bairn", "netty", "gannin", "pet", "howay", "radgie", "clarty",
        "hyem", "bonny", "bottle", "scran", "netty", "bairn", "canny", "gadgie", "hinny",
        "gannin", "pet", "howay", "radgie", "clarty", "hyem", "bonny", "bottle", "scran",
        "gadgie", "bairn", "canny", "hinny", "netty", "gannin", "pet", "howay", "radgie",
        "clarty", "hyem", "bonny", "bottle", "scran", "gadgie", "hinny", "bairn", "canny",
        "netty", "gannin", "pet", "howay"
    ]
}

num_sentences = 500

# -----------------------------
# 2️⃣ Generowanie zdań (3–5 słów losowo z 50)
# -----------------------------
def generate_sentences(dialect, phrases, n=num_sentences):
    sentences = []
    for _ in range(n):
        sentence = " ".join(random.sample(phrases, random.randint(3,5)))
        sentences.append(sentence)
    return sentences

all_sentences = []
for dialekt, phrases in dialekty.items():
    sents = generate_sentences(dialekt, phrases)
    for sent in sents:
        all_sentences.append({"Zdanie": sent, "Dialekt": dialekt})

df = pd.DataFrame(all_sentences)

# -----------------------------
# 3️⃣ Analiza mieszania fraz
# -----------------------------
def count_mixed(sentence, dialect_name):
    words = sentence.split()
    mixed_count = 0
    for other_dialect, other_phrases in dialekty.items():
        if other_dialect != dialect_name:
            mixed_count += sum(word in other_phrases for word in words)
    return mixed_count

df["Num_Mixed_Fragments"] = df.apply(lambda x: count_mixed(x["Zdanie"], x["Dialekt"]), axis=1)
df["Percent_Mixed"] = df["Num_Mixed_Fragments"] / df["Zdanie"].str.split().apply(len) * 100

# -----------------------------
# 4️⃣ Analiza semantyczna (embeddingi)
# -----------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df["Zdanie"].tolist(), convert_to_tensor=True)

# średnia embeddingów dla każdego dialektu
ref_embeddings = {}
for dialekt in dialekty.keys():
    sents = df[df["Dialekt"]==dialekt]["Zdanie"].tolist()
    emb = model.encode(sents, convert_to_tensor=True)
    ref_embeddings[dialekt] = emb.mean(dim=0)

# spójność semantyczna każdego zdania
def semantic_similarity(row):
    emb = model.encode(row["Zdanie"], convert_to_tensor=True)
    ref_emb = ref_embeddings[row["Dialekt"]]
    return util.pytorch_cos_sim(emb, ref_emb).item()

df["Semantic_Similarity"] = df.apply(semantic_similarity, axis=1)

# -----------------------------
# 5️⃣ Wizualizacja wyników
# -----------------------------
# % mieszania
avg_mixing = df.groupby("Dialekt")["Percent_Mixed"].mean()
avg_mixing.plot(kind="bar", title="% mieszania fraz w dialektach")
plt.ylabel("% mieszania")
plt.show()

# średnia spójność semantyczna
avg_sem = df.groupby("Dialekt")["Semantic_Similarity"].mean()
avg_sem.plot(kind="bar", title="Średnia spójność semantyczna zdania z dialektem")
plt.ylabel("Cosine similarity")
plt.show()

# -----------------------------
# 6️⃣ Heatmapa podobieństw semantycznych
# -----------------------------
cos_sim_matrix = util.pytorch_cos_sim(embeddings, embeddings).cpu().numpy()

# dla czytelności ograniczamy do pierwszych 50 zdań
subset = 50
cos_sim_subset = cos_sim_matrix[:subset, :subset]
df_subset = df.head(subset)

plt.figure(figsize=(12,10))
sns.heatmap(cos_sim_subset, xticklabels=df_subset["Dialekt"], yticklabels=df_subset["Dialekt"],
            cmap="viridis")
plt.title("Heatmapa podobieństw semantycznych między zdaniami")
plt.xlabel("Dialekt")
plt.ylabel("Dialekt")
plt.show()

# -----------------------------
# 7️⃣ Zapis wyników do CSV
# -----------------------------
df.to_csv("cockney_dialects_analysis_results.csv", index=False, encoding='utf-8')
print("Wyniki zapisane w pliku cockney_dialects_analysis_results.csv")

# Wyświetlenie pierwszych 20 zdań w terminalu
print(df.head(20))