from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from .song_similarity import Song as SongClass, cosine_similarity, SongMatcher, SongPredictor
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from .data_structures import *

import kagglehub

# Download and load the dataset
dataset_path = kagglehub.dataset_download('maharshipandya/-spotify-tracks-dataset')
df = pd.read_csv(f"{dataset_path}/dataset.csv")

## Cleaning Dataset ##

# Remove duplicates and missing values
df = df.dropna()
df = df.drop_duplicates(subset=['track_name', 'artists'], keep='first')

# These are the features I will be using for cosine similarity
feature_cols = ['danceability', 'energy', 'key', 'loudness', 'speechiness',
                'time_signature', 'acousticness', 'instrumentalness',
                'liveness', 'valence', 'tempo']

# Encode the track genre because it's categorical
df = pd.get_dummies(df, columns=['track_genre'], prefix='genre')

# Get all genre columns that were created
genre_cols = [col for col in df.columns if col.startswith('genre_')]

# Combine numeric features with encoded genres
all_feature_cols = feature_cols + genre_cols

# Normalize features to 0-1 scale for fair comparison
scaler = MinMaxScaler()
df[all_feature_cols] = scaler.fit_transform(df[all_feature_cols])

# Keep metadata columns
df_clean = df[['track_id', 'track_name', 'artists'] + all_feature_cols].copy()

# Create a list of Song objects for easy access
song_database = []
song_name_bst = BST()  # BST for fast song name lookups
search_trie = SongSearchTrie() #Trie for prefix search
# Create BSTs indexed by key features for efficient range filtering
# Using composite score (average of danceability, energy, valence)
feature_bst = BST()  # BST indexed by composite feature score

print("Building song database and feature indices...")
for idx, row in df_clean.iterrows():
    features = row[all_feature_cols].values.tolist()
    song_obj = SongClass(
        song_id=row['track_id'],
        name=row['track_name'],
        artist=row['artists'],
        features=features
    )
    song_database.append(song_obj)

    # Index by lowercase name for case-insensitive search
    song_name_bst.insert(row['track_name'].lower(), song_obj)

    # Index by composite feature score (danceability + energy + valence average)
    composite_score = (features[0] + features[1] + features[9]) / 3.0
    feature_bst.insert(composite_score, song_obj)
    #Insert into trie for prefix search
    search_trie.insert(song_obj)

print(f"Indexed {len(song_database)} songs with BST feature indexing")

#Initialize song predictor
song_predictor = SongPredictor(song_database)

app = FastAPI(title="MelodyMatchr API",
              description="Simple endpoints for computing song similarity and matching",
              version="0.1")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SongModel(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    artist: Optional[str] = None
    features: List[float]
class SimilarityRequest(BaseModel):
    song1: SongModel
    song2: SongModel

class MatchRequest(BaseModel):
    target: SongModel
    candidates: List[SongModel]
    top_k: Optional[int] = 5

class SearchRequest(BaseModel):
    song_name: str
    top_k: Optional[int] = 3

def to_internal_song(m: SongModel) -> SongClass:
    return SongClass(song_id=m.id, name=m.name or "", artist=m.artist or "", features=m.features)

class PrefixSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class PredictRequest(BaseModel):
    song: SongModel
    tolerance: Optional[float] = 0.1
    top_k: Optional[int] = 5

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/similarity")
async def similarity(req: SimilarityRequest):
    s1 = to_internal_song(req.song1)
    s2 = to_internal_song(req.song2)
    sim = cosine_similarity(s1, s2).compute()
    return {"similarity": sim}


@app.post("/match")
async def match(req: MatchRequest):
    target = to_internal_song(req.target)
    candidates = [to_internal_song(c) for c in req.candidates]

    top_k = max(1, int(req.top_k or 5))

    # Use SongMatcher class from song_similarity.py
    matcher = SongMatcher(target, candidates)
    results = matcher.match(top_k=top_k)

    # Format results
    matches = []
    for similarity, song in results:
        matches.append({
            "id": song.id,
            "name": song.name,
            "artist": song.artist,
            "similarity": similarity
        })

    return {"matches": matches}


@app.post("/search")
async def search(req: SearchRequest):
    """
    Search for a song by name and return top K similar songs from the database.
    Uses BST for exact match lookup, falls back to linear search for partial matches.
    """
    query = req.song_name.lower().strip()

    if not query:
        raise HTTPException(status_code=400, detail="Song name cannot be empty")

    # Try exact match using BST first (O(log n))
    target_song = song_name_bst.search(query)

    # If no exact match, fall back to partial match using linear search
    if not target_song:
        for song in song_database:
            if query in song.name.lower():
                target_song = song
                break

    if not target_song:
        raise HTTPException(status_code=404, detail=f"Song '{req.song_name}' not found in database")

    # Calculate target song's composite score
    target_composite = (target_song.features[0] + target_song.features[1] + target_song.features[9]) / 3.0

    # Use BST range_search to filter candidates within similar feature range
    # Only search songs within ±0.2 (chosen after testing different values) of target's composite score
    range_tolerance = 0.2
    min_score = max(0.0, target_composite - range_tolerance)
    max_score = min(1.0, target_composite + range_tolerance)

    # Get candidate songs using BST range search (much faster than full scan)
    candidates = feature_bst.range_search(min_score, max_score)

    # Remove target song from candidates if present
    candidates = [song for song in candidates if song.id != target_song.id]

    # If we didn't get enough candidates from range search, expand range
    if len(candidates) < 100:
        range_tolerance = 0.4
        min_score = max(0.0, target_composite - range_tolerance)
        max_score = min(1.0, target_composite + range_tolerance)
        candidates = feature_bst.range_search(min_score, max_score)
        candidates = [song for song in candidates if song.id != target_song.id]

    top_k = max(1, int(req.top_k or 3))

    # Use SongMatcher class from song_similarity.py on filtered candidates
    matcher = SongMatcher(target_song, candidates)
    results = matcher.match(top_k=top_k)

    # Format results
    matches = []
    for similarity, song in results:
        matches.append({
            "id": song.id,
            "name": song.name,
            "artist": song.artist,
            "similarity": similarity
        })

    return {
        "searched_song": {
            "id": target_song.id,
            "name": target_song.name,
            "artist": target_song.artist
        },
        "matches": matches
    }

@app.post("/search/prefix")
async def prefix_search(req: PrefixSearchRequest):
    """
    Search for songs by prefix using Trie data structure.
    Returns songs whose names start with the given query string.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = search_trie.search_prefix(req.query, max_results=req.max_results or 5)
    
    return {
        "query": req.query,
        "results": [
            {"id": song.id, "name": song.name, "artist": song.artist} 
            for song in results
        ]
    }


# NEW: Predict similar songs endpoint
@app.post("/predict")
async def predict_similar_songs(req: PredictRequest):
    """
    Predict similar songs based on features using the SongPredictor.
    """
    target = to_internal_song(req.song)
    
    results = song_predictor.predict_similar(
        target, 
        tolerance=req.tolerance or 0.1,
        top_k=req.top_k or 5
    )
    
    return {
        "predictions": [
            {
                "id": song.id,
                "name": song.name,
                "artist": song.artist,
                "similarity": score
            }
            for score, song in results
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=True)
