from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


from song_similarity import Song as SongClass, cosine_similarity
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from data_structures import *

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

for idx, row in df_clean.iterrows():
    features = row[all_feature_cols].values.tolist()
    song_obj = SongClass(
        song_id=row['track_id'],
        name=row['track_name'],
        artist=row['artists'],
        features=features
    )
    song_database.append(song_obj)






app = FastAPI(title="MelodyMatchr API",
              description="Simple endpoints for computing song similarity and matching",
              version="0.1")


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


def to_internal_song(m: SongModel) -> SongClass:
    return SongClass(song_id=m.id, name=m.name or "", artist=m.artist or "", features=m.features)


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

    scored = []
    for cand in candidates:
        score = cosine_similarity(target, cand).compute()
        scored.append({"id": cand.id, "name": cand.name, "artist": cand.artist, "similarity": score})

    # sort descending by similarity
    scored.sort(key=lambda x: x["similarity"], reverse=True)

    top_k = max(1, int(req.top_k or 5))
    return {"matches": scored[:top_k]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("melodymatchr.api.app:app", host="127.0.0.1", port=8000, log_level="info")
