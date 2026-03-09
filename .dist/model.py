import kagglehub
import pandas as pd
import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# load dataset
path = kagglehub.dataset_download("jainamgada45/indian-government-schemes")

files = os.listdir(path)
df = pd.read_csv(os.path.join(path, files[0]))

df = df.fillna("Not specified")

# combine text
df["combined_text"] = (
    df["scheme_name"] + " " +
    df["details"] + " " +
    df["benefits"] + " " +
    df["eligibility"] + " " +
    df["schemeCategory"] + " " +
    df["tags"]
)

# clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text

df["clean_text"] = df["combined_text"].apply(clean_text)

# load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# file to store embeddings
embedding_file = "scheme_embeddings.npy"

# compute embeddings only if file doesn't exist
if os.path.exists(embedding_file):

    print("Loading saved embeddings...")
    scheme_embeddings = np.load(embedding_file)

else:

    print("Computing embeddings (first run only)...")
    scheme_embeddings = model.encode(df["clean_text"].tolist())

    np.save(embedding_file, scheme_embeddings)

    print("Embeddings saved!")



def find_schemes(query):

    query_embedding = model.encode([query])

    scores = cosine_similarity(query_embedding, scheme_embeddings)

    top_indices = scores[0].argsort()[-3:][::-1]

    results = []

    for i in top_indices:
        scheme = df.iloc[i]

        results.append({
            "name": scheme["scheme_name"],
            "category": scheme["schemeCategory"],
            "eligibility": scheme["eligibility"][:200],
            "benefits": scheme["benefits"][:200],
            "about": scheme["details"][:200]
        })

    return results