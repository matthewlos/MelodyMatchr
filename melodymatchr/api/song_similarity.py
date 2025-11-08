
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from data_structures import MinHeap

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
    def __init__(self, target_song, candidate_songs, artist_weight=0.1):
        self.target_song = target_song
        self.candidate_songs = candidate_songs
        self.artist_weight = artist_weight  # Bonus for same artist

    def match(self, top_k=5):
        heap = MinHeap(max_size=top_k)

        for candidate in self.candidate_songs:
            # Compute base cosine similarity
            sim = cosine_similarity(self.target_song, candidate).compute()

            # Add artist bonus: if same artist, boost similarity
            if self.target_song.artist == candidate.artist:
                sim = min(1.0, sim + self.artist_weight)  # Cap at 1.0

            heap.insert(sim, candidate)

        results = []
        while len(heap.heap) > 0:
            results.append(heap.extract_min())

        results.reverse()
        return results