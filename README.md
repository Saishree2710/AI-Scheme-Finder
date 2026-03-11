# AI Government Scheme Finder 🇮🇳
AI Government Scheme Finder is a machine learning based web application that helps users discover relevant Indian government schemes using natural language queries.

## Features
- Natural language scheme search
- Machine learning powered recommendations
- Fast similarity search using embeddings
- Simple web interface

## Tech Stack
- Python
- Flask
- Sentence Transformers
- Scikit-learn
- Pandas
- HTML / CSS / Bootstrap

## Machine Learning Model
This project uses the `all-MiniLM-L6-v2` sentence transformer model to convert scheme descriptions and user queries into embeddings.

Cosine similarity is used to recommend the most relevant schemes.

## Project Structure
AI-Scheme-Finder
│
├── app.py
├── model.py
│
├── static
│
├── templates
│
└── scheme_embeddings.npy

## Run Locally

Clone the repository:

```
git clone https://github.com/Saishree2710/AI-Scheme-Finder.git
cd AI-Scheme-Finder
```

Install dependencies:

```
pip install flask pandas numpy scikit-learn sentence-transformers kagglehub reportlab
```

Run the application:

```
python app.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

