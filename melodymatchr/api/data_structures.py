## The Data structures for MelodyMatchr

class MinHeap:

    def __init__(self, max_size=10):
        self.heap = []
        self.max_size = max_size

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def heapify_up(self, i):
        while i > 0 and self.heap[i][0] < self.heap[self.parent(i)][0]:
            parent_idx = self.parent(i)
            self.swap(i, parent_idx)
            i = parent_idx

    def heapify_down(self, i):
        min_idx = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.heap[left][0] < self.heap[min_idx][0]:
            min_idx = left

        if right < len(self.heap) and self.heap[right][0] < self.heap[min_idx][0]:
            min_idx = right

        if min_idx != i:
            self.swap(i, min_idx)
            self.heapify_down(min_idx)

    def insert(self, similarity_score, song_data):

        if len(self.heap) < self.max_size:
            self.heap.append((similarity_score, song_data))
            self.heapify_up(len(self.heap) - 1)
        elif similarity_score > self.heap[0][0]:
            self.heap[0] = (similarity_score, song_data)
            self.heapify_down(0)

    def get_min(self):
        return self.heap[0] if self.heap else None

    def extract_min(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapify_down(0)
        return min_val

    def get_sorted_results(self):
        results = []
        temp_heap = self.heap.copy()

        while self.heap:
            results.append(self.extract_min())

        self.heap = temp_heap
        return results


class BSTNode:

    def __init__(self, key, song_data):
        self.key = key
        self.song_data = song_data
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, key, song_data):
        """Insert a song with a key value"""
        self.root = self._insert_recursive(self.root, key, song_data)
        self.size += 1

    def _insert_recursive(self, node, key, song_data):
        if node is None:
            return BSTNode(key, song_data)

        if key < node.key:
            node.left = self._insert_recursive(node.left, key, song_data)
        else:
            node.right = self._insert_recursive(node.right, key, song_data)
        return node

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        if node is None or node.key == key:
            return node.song_data if node else None

        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)

    def range_search(self, min_key, max_key):

        results = []
        self._range_search_recursive(self.root, min_key, max_key, results)
        return results

    def _range_search_recursive(self, node, min_key, max_key, results):
        if node is None:
            return

        if min_key <= node.key <= max_key:
            results.append(node.song_data)

        if node.key > min_key:
            self._range_search_recursive(node.left, min_key, max_key, results)

        if node.key < max_key:
            self._range_search_recursive(node.right, min_key, max_key, results)

    def inorder_traversal(self):
        results = []
        self._inorder_recursive(self.root, results)
        return results

    def _inorder_recursive(self, node, results):
        if node is None:
            return

        self._inorder_recursive(node.left, results)
        results.append((node.key, node.song_data))
        self._inorder_recursive(node.right, results)


def binary_search(sorted_array, target, key_func=lambda x: x):

    left, right = 0, len(sorted_array) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = key_func(sorted_array[mid])

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_range(sorted_array, min_val, max_val, key_func=lambda x: x):

    # Find leftmost position >= min_val
    left = 0
    right = len(sorted_array)

    while left < right:
        mid = (left + right) // 2
        if key_func(sorted_array[mid]) < min_val:
            left = mid + 1
        else:
            right = mid

    start_idx = left

    left = 0
    right = len(sorted_array)

    while left < right:
        mid = (left + right) // 2
        if key_func(sorted_array[mid]) <= max_val:
            left = mid + 1
        else:
            right = mid

    end_idx = left

    return sorted_array[start_idx:end_idx]

#Added For improved search functionality **(optional)** DELETE or FIX if broken

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.songs = []  # Store song objects that match this prefix

class SongSearchTrie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, song):
        """Insert song name for autocomplete"""
        name = song.name.lower()
        node = self.root
        
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