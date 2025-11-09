# MelodyMatchr

A song recommendation app that uses different data structures (MinHeap and HashTable) to find similar songs based on audio features.

## Features

- **Song Search**: Find similar songs using two different algorithms
  - MinHeap: O(n log k) - Efficient for smaller k values
  - HashTable: O(n + k log k) - Better for larger k values
- **Autocomplete**: Smart prefix search using Trie data structure
- **Performance Comparison**: See execution time for each algorithm
- **Adjustable Recommendations**: Slider to request 3-30 song recommendations

## Tech Stack

**Frontend:**
- Next.js (React)
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI (Python)
- Custom Data Structures (MinHeap, HashTable, BST, Trie)
- Kaggle Dataset (Spotify Tracks)

## Getting Started

### Prerequisites

- Python 3.x
- Node.js and npm
- pip (Python package manager)

### Installation

1. **Install Python dependencies:**

```bash
cd melodymatchr/api
pip install -r requirements.txt
```

2. **Install Node.js dependencies:**

```bash
cd melodymatchr
npm install
```

### Running the Application

**Step 1: Start the FastAPI Backend**

```bash
cd melodymatchr/api
python app.py
```

The API will start on `http://localhost:8000`

**Step 2: Start the Next.js Frontend**

In a new terminal:

```bash
cd melodymatchr
npm run dev
```

The frontend will start on `http://localhost:3000`

**Step 3: Open the Application**

Open [http://localhost:3000](http://localhost:3000) in your browser.

## How to Use

1. Use the slider to select how many recommendations you want (3-30)
2. Choose your algorithm (MinHeap or HashTable)
3. Start typing a song name - autocomplete suggestions will appear
4. Click Search or press Enter
5. View the recommendations and execution time
6. Compare performance between algorithms with different k values!

## Data Structures Used

- **MinHeap**: Top-k selection with minimal memory (O(k) space)
- **HashTable**: Bucket-based top-k with faster insertion (O(n) space)
- **BST (Binary Search Tree)**: Fast song lookup and range queries
- **Trie**: Prefix-based autocomplete search
