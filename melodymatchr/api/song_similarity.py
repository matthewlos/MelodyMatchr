

import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from data_structures import MinHeap, BST, HashTableTopK


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
    
    # MinHeap implementation for finding top-k similar songs.
    # Time: O(n log k), Space: O(k)
    
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

# TODO: Implement HashTable version  of above SongMatcher for faster top-k retrieval #









# END Implement HashTable version (We don't need to implement HashTable version for the Predictor) #

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
