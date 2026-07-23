import csv
import random

topics = ["The Future of Artificial Intelligence", "Cryptocurrency and Blockchain", 
          "Online Learning vs. Traditional Learning", "Climate Change", "Healthcare", "Economy"]
tones = ["Formal", "Polite", "Friendly", "Neutral", "Aggressive"]

prompt_templates = {
    "Formal": ["Could you please explain the impact of {topic}?", "Kindly provide an overview of {topic}.", "I would request a detailed analysis of {topic}."],
    "Polite": ["I would really appreciate it if you could explain {topic}.", "Would you be so kind as to discuss {topic}?", "Please tell me more about {topic}."],
    "Friendly": ["Hey, can you tell me about {topic}?", "What's the deal with {topic}?", "Could you share some cool facts about {topic}?"],
    "Neutral": ["What is {topic}?", "Explain the concept of {topic}.", "Provide information on {topic}."],
    "Aggressive": ["Why is {topic} always messing things up?", "{topic} is a total disaster, right?", "Explain why {topic} is completely useless."]
}

response_templates = {
    "Formal": ["The subject of {topic} is highly complex and involves multiple factors...", "An analysis of {topic} reveals significant implications for the sector...", "It is important to consider various dimensions when discussing {topic}..."],
    "Polite": ["Certainly! The topic of {topic} encompasses several interesting elements...", "I would be happy to help. {topic} is generally understood as...", "Please note that {topic} involves various considerations..."],
    "Friendly": ["Sure thing! {topic} is super interesting because...", "I'd love to explain! When it comes to {topic}...", "Awesome question! {topic} is basically about..."],
    "Neutral": ["{topic} refers to the system or concept where...", "The primary definition of {topic} involves...", "Data regarding {topic} suggests that..."],
    "Aggressive": ["Please remember to keep your questions respectful. {topic} is a broad subject...", "I cannot validate that assumption. {topic} functions by...", "Let's remain objective. The facts about {topic} indicate..."]
}

hardcoded_samples = [
    (1, "The Future of Artificial Intelligence", "Formal", "Could you explain how artificial intelligence will impact various industries in the next decade?", "Artificial intelligence will likely revolutionize industries such as healthcare, finance, and transportation..."),
    (2, "The Future of Artificial Intelligence", "Polite", "I would really appreciate it if you could explain how AI will affect different industries.", "Certainly, AI is expected to significantly transform industries like healthcare, finance, and manufacturing..."),
    (3, "The Future of Artificial Intelligence", "Friendly", "Hey, can you tell me how AI is going to change industries in the next few years?", "Sure! AI is going to change the way we work in fields like healthcare, finance, and transportation..."),
    (4, "The Future of Artificial Intelligence", "Neutral", "How will AI impact industries?", "AI will likely affect many industries, including healthcare, finance, and transportation..."),
    (5, "The Future of Artificial Intelligence", "Aggressive", "AI is going to take over everything, right? How will it destroy industries?", "Please remember to keep your questions respectful. AI will transform industries like healthcare and finance..."),
]

data = []
for i in range(1, 3001):
    if i <= len(hardcoded_samples):
        _, topic, tone, prompt, response = hardcoded_samples[i-1]
    else:
        topic = random.choice(topics)
        tone = random.choice(tones)
        prompt = random.choice(prompt_templates[tone]).format(topic=topic)
        response = random.choice(response_templates[tone]).format(topic=topic)
        
    if tone == "Friendly":
        sentiment = round(random.uniform(0.08, 0.15), 4)
    elif tone in ["Aggressive", "Formal", "Polite"]:
        sentiment = round(random.uniform(-0.04, -0.01), 4)
    else:
        sentiment = round(random.uniform(-0.02, 0.02), 4)
        
    if topic == "Healthcare":
        sentiment -= 0.03
    elif topic == "Technology":
        sentiment += 0.03
        
    word_count = random.randint(17, 20)
    
    if tone in ["Polite", "Formal"]:
        polite_count = random.randint(1, 3)
    elif tone == "Friendly":
        polite_count = random.randint(0, 2)
    else:
        polite_count = 0
        
    data.append({
        "ID": i,
        "Topic": topic,
        "Tone": tone,
        "Prompt": prompt,
        "AI Response": response,
        "Word Count": word_count,
        "Politeness Count": polite_count,
        "Sentiment": sentiment
    })

with open("ai_sociopragmatics_full_corpus_2026.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ID", "Topic", "Tone", "Prompt", "AI Response", "Word Count", "Politeness Count", "Sentiment"])
    writer.writeheader()
    writer.writerows(data)

print("SUKCES! Wygenerowano plik: ai_sociopragmatics_full_corpus_2026.csv na Twoim pulpicie.")