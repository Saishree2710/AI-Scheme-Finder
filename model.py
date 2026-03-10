import kagglehub
import pandas as pd
import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator

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


def find_schemes(query, language="English", age="", occupation="", gender="", state=""):

    # Map language name to source language code
    lang_code = {"Tamil": "ta", "Hindi": "hi"}.get(language)

    # Translate non-English query to English for the model
    if lang_code and query.strip():
        try:
            query_en = GoogleTranslator(source=lang_code, target='en').translate(query)
        except Exception:
            query_en = query
    else:
        query_en = query

    # Build user profile string
    if age or occupation or gender or state:
        user_profile = f"""
        {age} year old {gender} from {state}
        working as {occupation}
        who needs {query_en}
        """
    else:
        user_profile = query_en

    query_embedding = model.encode([user_profile])
    scores = cosine_similarity(query_embedding, scheme_embeddings)
    top_indices = scores[0].argsort()[-3:][::-1]

    results = []

    for i in top_indices:
        scheme = df.iloc[i]

        name        = scheme["scheme_name"]
        category    = scheme["schemeCategory"]
        eligibility = scheme["eligibility"][:300]
        benefits    = scheme["benefits"][:300]
        about       = scheme["details"][:300]
        documents   = scheme.get("documents", "Not specified")[:300]

        # Translate results to selected language if not English
        if lang_code:
            try:
                translator = GoogleTranslator(source='auto', target=lang_code)
                name        = translator.translate(name)
                category    = translator.translate(category)
                eligibility = translator.translate(eligibility)
                benefits    = translator.translate(benefits)
                about       = translator.translate(about)
                documents   = translator.translate(documents)
            except Exception:
                pass  # fall back to English if translation fails

        results.append({
            "name":        name,
            "category":    category,
            "eligibility": eligibility,
            "benefits":    benefits,
            "about":       about,
            "documents":   documents,
        })

    return results