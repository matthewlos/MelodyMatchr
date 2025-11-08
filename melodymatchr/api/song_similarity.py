

import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from .data_structures import MinHeap, BST


class Song:

    def __init__(self, song_id, name, artist, features):
        self.id = song_id
        self.name = name
        self.artist = artist
        self.features = features

    def __repr__(self):
        return f"Song('{self.name}' by {self.artist})"


class cosine_similarity:
    def __init__(self, song1, song2):
        self.song1 = song1
        self.song2 = song2

    def compute(self):
        dot_product = sum(a * b for a, b in zip(self.song1.features, self.song2.features))
        magnitude1 = math.sqrt(sum(a ** 2 for a in self.song1.features))
        magnitude2 = math.sqrt(sum(b ** 2 for b in self.song2.features))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

class SongMatcher:
    def __init__(self, target_song, candidate_songs):
        self.target_song = target_song
        self.candidate_songs = candidate_songs

    def match(self, top_k=5):
        heap = MinHeap(max_size=top_k)

        for candidate in self.candidate_songs:
            sim = cosine_similarity(self.target_song, candidate).compute()
            heap.insert(sim, candidate)

        results = []
        while len(heap.heap) > 0:
            results.append(heap.extract_min())

        results.reverse()
        return results

# This is for the pridictive typing feature if fails DELETE or FIX 
class SongPredictor:
    def __init__(self, song_database):
        self.songs = song_database
        self.feature_bst = None
        self._build_indices()
    
    def _build_indices(self):
        """Build BST index on key features for fast lookup"""
        self.feature_bst = BST()
        for song in self.songs:
            if song.features:  
                key = song.features[0]  
                self.feature_bst.insert(key, song)
    
    def predict_similar(self, target_song, tolerance=0.1, top_k=10):
        """Predict similar songs using feature range search"""
        
        if not target_song.features:
            return []
        
        key_feature = target_song.features[0]
        min_key = key_feature - tolerance
        max_key = key_feature + tolerance
        
        
        candidates = self.feature_bst.range_search(min_key, max_key)
        
        
        heap = MinHeap(max_size=top_k)
        for candidate in candidates:
            if candidate.id != target_song.id:
                sim = cosine_similarity(target_song, candidate).compute()
                heap.insert(sim, candidate)
        
        results = []
        while len(heap.heap) > 0:
            results.append(heap.extract_min())
        
        results.reverse()
        return results

def load_songs_from_dataset(dataset_path: str, song_class):  # Rename parameter
    import pandas as pd 
    import os
    csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {dataset_path}")
    df = pd.read_csv(os.path.join(dataset_path, csv_files[0]))
    songs = []
    
    feature_columns = [
        'danceability', 'energy', 'loudness', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 
        'valence', 'tempo'
    ]
    
    available_features = [col for col in feature_columns if col in df.columns]
    
    for idx, row in df.iterrows():
        try:
            features = [float(row.get(col, 0.0)) if not pd.isna(row.get(col, 0.0)) else 0.0 
                       for col in available_features]
            
            song_id = str(row.get('track_id', row.get('id', idx)))
            name = str(row.get('track_name', row.get('name', 'Unknown')))
            artist = str(row.get('artists', row.get('artist', 'Unknown Artist')))
            
            song_obj = song_class(song_id=song_id, name=name, artist=artist, features=features)
            songs.append(song_obj)
        except Exception as e:
            continue
    
    print(f"Loaded {len(songs)} songs from dataset")
    return songs