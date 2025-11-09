import math
from data_structures import MinHeap, HashTableTopK

# Define a simple Song class to hold song information
class Song:

    # Initialize the Song object with id, name, artist, and feature vector.
    def __init__(self, song_id, name, artist, features):
        self.id = song_id
        self.name = name
        self.artist = artist
        self.features = features

    # String representation of the Song object.
    def __repr__(self):
        return f"Song('{self.name}' by {self.artist})"

# Define cosine similarity between two songs
class cosine_similarity:
    def __init__(self, song1, song2):
        self.song1 = song1
        self.song2 = song2

    # Compute the cosine similarity score.
    def compute(self):
        # Calculate the dot product and magnitudes
        dot_product = sum(a * b for a, b in zip(self.song1.features, self.song2.features))
        magnitude1 = math.sqrt(sum(a ** 2 for a in self.song1.features))
        magnitude2 = math.sqrt(sum(b ** 2 for b in self.song2.features))

        # Handle edge case of zero magnitude
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Compute the cosine similarity
        return dot_product / (magnitude1 * magnitude2)

# SongMatcher using MinHeap for top-k similar songs
class SongMatcher:
    
    # MinHeap implementation for finding top-k similar songs.
    # Time: O(n log k), Space: O(k)
    
    def __init__(self, target_song, candidate_songs):
        self.target_song = target_song
        self.candidate_songs = candidate_songs

    # Match and return top-k similar songs
    def match(self, top_k=5):
        heap = MinHeap(max_size=top_k)

        # Compute similarities and maintain top-k in the heap
        for candidate in self.candidate_songs:
            # Calculate similarity
            sim = cosine_similarity(self.target_song, candidate).compute()
            heap.insert(sim, candidate)

        # Extract results from heap in descending order
        results = []
        while len(heap.heap) > 0:
            # Get the minimum (least similar) from the heap
            results.append(heap.extract_min())

        # Reverse to have highest similarity first
        results.reverse()
        return results

# TODO: Implement HashTable version  of above SongMatcher for faster top-k retrieval #

class SongMatcherHashTable:
    
    # HashTable implementation for finding top-k similar songs.
    # Time: O(n + k log k), Space: O(n)
    
    def __init__(self, target_song, candidate_songs):
        self.target_song = target_song
        self.candidate_songs = candidate_songs
    
    # match and return top-k similar songs
    def match(self, top_k=5):
        hash_table = HashTableTopK(num_buckets=100)
        for candidate in self.candidate_songs:
            sim = cosine_similarity(self.target_song, candidate).compute()
            hash_table.insert(sim, candidate)
        
        return hash_table.get_top_k(top_k)
    
# END Implement HashTable version #



