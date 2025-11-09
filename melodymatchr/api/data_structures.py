## The Data structures for MelodyMatchr

# MinHeap Implementation - Useful for finding the top-k similar songs
# A maxheap would not drop the lowest similarity scores when full
class MinHeap:

    # Initialize the MinHeap with an optional maximum size.
    def __init__(self, max_size=10):
        self.heap = []
        self.max_size = max_size

    # Helper methods to get parent and child indices
    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    # Swap two elements in the heap
    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    # Maintain the heap property by moving the element at index i up.
    def heapify_up(self, i):
        while i > 0 and self.heap[i][0] < self.heap[self.parent(i)][0]:
            parent_idx = self.parent(i)
            self.swap(i, parent_idx)
            i = parent_idx

    # Maintain the heap property by moving the element at index i down.
    def heapify_down(self, i):
        min_idx = i
        left = self.left_child(i)
        right = self.right_child(i)

        # Check if left child exists and is smaller than current minimum
        if left < len(self.heap) and self.heap[left][0] < self.heap[min_idx][0]:
            min_idx = left

        # Check if right child exists and is smaller than current minimum
        if right < len(self.heap) and self.heap[right][0] < self.heap[min_idx][0]:
            min_idx = right

        # If the minimum is not the current index, swap and continue heapifying down
        if min_idx != i:
            self.swap(i, min_idx)
            self.heapify_down(min_idx)

    # Insert a new (similarity_score, song_data) tuple into the heap.
    def insert(self, similarity_score, song_data):

        # If heap is not full, add the new item
        if len(self.heap) < self.max_size:
            self.heap.append((similarity_score, song_data))
            self.heapify_up(len(self.heap) - 1)
        # If the new item is larger than the minimum, replace and heapify down
        elif similarity_score > self.heap[0][0]:
            self.heap[0] = (similarity_score, song_data)
            self.heapify_down(0)

    # Get the minimum element (root) of the heap without removing it.
    def get_min(self):
        return self.heap[0] if self.heap else None

    # Extract and return the minimum element from the heap.
    def extract_min(self):
        if not self.heap:
            return None

        # If only one element, pop and return it
        if len(self.heap) == 1:
            return self.heap.pop()

        # Remove and return the root element
        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapify_down(0)
        return min_val

    # Get all elements in the heap sorted by similarity score.
    def get_sorted_results(self):
        results = []
        temp_heap = self.heap.copy()

        while self.heap:
            results.append(self.extract_min())

        self.heap = temp_heap
        return results


# Binary Search Tree (BST) Implementation
# Node class for BST
class BSTNode:

    # Node initialization
    def __init__(self, key, song_data):
        self.key = key
        self.song_data = song_data
        self.left = None
        self.right = None


# Binary Search Tree (BST) class
class BST:
    # Initialize the BST.
    def __init__(self):
        self.root = None
        self.size = 0

    # Insert a new node into the BST.
    def insert(self, key, song_data):
        """Insert a song with a key value"""
        # If the tree is empty, create the root
        self.root = self._insert_recursive(self.root, key, song_data)
        self.size += 1

    # Helper method for recursive insertion
    def _insert_recursive(self, node, key, song_data):
        if node is None:
            return BSTNode(key, song_data)
        # Insert in left or right subtree
        if key < node.key:
            node.left = self._insert_recursive(node.left, key, song_data)
        else:
            node.right = self._insert_recursive(node.right, key, song_data)
        return node

    # Search for a node with the given key.
    def search(self, key):
        return self._search_recursive(self.root, key)

    # Helper method for recursive search
    def _search_recursive(self, node, key):
        if node is None or node.key == key:
            return node.song_data if node else None

        # Search in left or right subtree
        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)

    # Range search for keys between min_key and max_key (inclusive).
    def range_search(self, min_key, max_key):
        # Initialize results list
        results = []
        self._range_search_recursive(self.root, min_key, max_key, results)
        return results

    # Helper method for recursive range search
    def _range_search_recursive(self, node, min_key, max_key, results):
        if node is None:
            return

        # If current node's key is within range, add to results
        if min_key <= node.key <= max_key:
            results.append(node.song_data)

        # Traverse left subtree if potential keys exist
        if node.key > min_key:
            self._range_search_recursive(node.left, min_key, max_key, results)

        # Traverse right subtree if potential keys exist
        if node.key < max_key:
            self._range_search_recursive(node.right, min_key, max_key, results)

    # Inorder traversal of the BST (for testing/debugging)
    def inorder_traversal(self):
        results = []
        self._inorder_recursive(self.root, results)
        return results

    # Helper method for inorder traversal
    def _inorder_recursive(self, node, results):
        if node is None:
            return

        # Traverse left subtree
        self._inorder_recursive(node.left, results)
        results.append((node.key, node.song_data))
        self._inorder_recursive(node.right, results)


#Added For improved search functionality **(optional)** DELETE or FIX if broken

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.songs = []  # Store song objects that match this prefix

class SongSearchTrie:
    def __init__(self):
        self.root = TrieNode()
    
    # Insert a song into the trie
    def insert(self, song):
        """Insert song name for autocomplete"""
        name = song.name.lower()
        node = self.root
        
        # Insert each character of the song name
        for char in name:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.songs.append(song)  # Add to all prefix nodes
        
        node.is_end = True
    
    def search_prefix(self, prefix, max_results=10):
        """Return songs matching the prefix"""
        prefix = prefix.lower()
        node = self.root
        
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        return node.songs[:max_results]


# Hash Table for Top-K 
class HashTableTopK:
    # Hash Table-based data structure for finding top-k items.
    # Time Complexity:
      # - Insert: O(1) average - hash to bucket and append
      # - Get top-k: O(n + k log k) - scan buckets from high to low, sort within buckets
    # Space Complexity: O(n) - stores all items

    def __init__(self, num_buckets=100):
        self.num_buckets = num_buckets
        # Hash table: dictionary mapping bucket index to list of (similarity, song) tuples
        self.buckets = {}
        self.size = 0

    def _hash(self, similarity):
       
        bucket_index = int(similarity * self.num_buckets)
        # Handle edge case where similarity = 1.0
        if bucket_index >= self.num_buckets:
            bucket_index = self.num_buckets - 1
        return bucket_index

    def insert(self, similarity, song_data):
        ### Insert a song with its similarity score into the hash table.

        ### Time Complexity: O(1) average

        bucket_index = self._hash(similarity)

        # Create bucket if it doesn't exist
        if bucket_index not in self.buckets:
            self.buckets[bucket_index] = []

        # Append to bucket (chaining for collision resolution)
        self.buckets[bucket_index].append((similarity, song_data))
        self.size += 1

    def get_top_k(self, k):
        # retrieve top-k items with highest similarity scores
        results = []

        # Iterate from highest bucket to lowest
        for bucket_index in range(self.num_buckets - 1, -1, -1):
            if bucket_index in self.buckets:
                # Add all items from this bucket
                results.extend(self.buckets[bucket_index])

                # Early termination: if we have enough items
                if len(results) >= k:
                    # Sort collected items and return top k
                    results.sort(key=lambda x: x[0], reverse=True)
                    return results[:k]

        # If we collected fewer than k items, sort and return all
        results.sort(key=lambda x: x[0], reverse=True)
        return results

    def get_all_sorted(self):
        # gets songs with highest similarity in sorted order
        all_items = []
        for bucket in self.buckets.values():
            all_items.extend(bucket)

        all_items.sort(key=lambda x: x[0], reverse=True)
        return all_items

    def __len__(self):
        # num items in hash table
        return self.size
