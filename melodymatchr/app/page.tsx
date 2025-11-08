"use client";

import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [songName, setSongName] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // State for data structure selection
  const [dataStructure, setDataStructure] = useState<"minheap" | "hashtable">("minheap");
  
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Autocomplete with prefix search
  useEffect(() => {
    const controller = new AbortController();
    
    const fetchSuggestions = async () => {
      if (songName.trim().length < 2) {
        setSuggestions([]);
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/search/prefix', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: songName,
            max_results: 5
          }),
          signal: controller.signal
        });

        if (response.ok) {
          const data = await response.json();
          setSuggestions(data.results || []);
          setShowSuggestions(true);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('Autocomplete error:', error);
        }
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);
    return () => {
      clearTimeout(debounceTimer);
      controller.abort();
    };
  }, [songName]);

  const handleSearch = async () => {
    if (!songName.trim()) return;

    setIsSearching(true);
    setShowSuggestions(false);

    try {
      // MODIFIED: Choose endpoint based on selected data structure
      const endpoint = dataStructure === "hashtable" 
        ? 'http://localhost:8000/search/hashtable'
        : 'http://localhost:8000/search';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          song_name: songName,
          top_k: 3
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch recommendations');
      }

      const data = await response.json();
      setResults({
        searchedSong: data.searched_song.name,
        searchedArtist: data.searched_song.artist,
        matches: data.matches || [],
        dataStructure: dataStructure
      });
    } catch (error: any) {
      console.error('Error:', error);
      alert(error.message || 'Could not find song or connect to server. Make sure FastAPI is running on port 8000.');
    } finally {
      setIsSearching(false);
    }
  };

 const handleSuggestionClick = (suggestion: any) => {
    // Fill in "Song Name - Artist Name" format to handle duplicates
    setSongName(`${suggestion.name} - ${suggestion.artist}`);
    setShowSuggestions(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <main className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-purple-600 dark:text-purple-400 mb-4">
            MelodyMatchr
          </h1>
          <p className="text-lg text-gray-700 dark:text-gray-300">
            Find similar songs instantly with smart autocomplete
          </p>
        </div>

        {/* Search Box */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter a song name
            </label>
            <div className="relative">
              <div className="flex gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={songName}
                  onChange={(e) => setSongName(e.target.value)}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="e.g., Blinding Lights"
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  disabled={isSearching}
                  autoComplete="off"
                />
                <button
                  onClick={handleSearch}
                  disabled={isSearching || !songName.trim()}
                  className="px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isSearching ? "Searching..." : "Search"}
                </button>
              </div>

              {/* Autocomplete Suggestions */}
              {showSuggestions && suggestions.length > 0 && (
                <div 
                  ref={suggestionsRef}
                  className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-700 rounded-lg shadow-xl border border-gray-200 dark:border-gray-600 max-h-60 overflow-y-auto"
                >
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      type="button"
                      className="w-full text-left px-4 py-3 hover:bg-purple-50 dark:hover:bg-gray-600 border-b border-gray-100 dark:border-gray-600 last:border-b-0 transition-colors"
                    >
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {suggestion.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {suggestion.artist}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Data Structure Selector */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Algorithm Selection
              </label>
              
              {/* Toggle Switch Option */}
              <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <button
                  type="button"
                  onClick={() => setDataStructure("minheap")}
                  className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                    dataStructure === "minheap"
                      ? "bg-purple-600 text-white shadow-lg"
                      : "bg-white dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-500"
                  }`}
                >
                  <div className="text-lg">MinHeap</div>
                  <div className="text-xs opacity-80 mt-1">O(n log k)</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setDataStructure("hashtable")}
                  className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                    dataStructure === "hashtable"
                      ? "bg-purple-600 text-white shadow-lg"
                      : "bg-white dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-500"
                  }`}
                >
                  <div className="text-lg">HashTable</div>
                  <div className="text-xs opacity-80 mt-1">O(n + k log k)</div>
                </button>
              </div>

              {/* Info text about selected algorithm */}
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                {dataStructure === "minheap" 
                  ? "MinHeap maintains top-k items efficiently with minimal memory usage"
                  : "HashTable provides faster retrieval by bucketing similarity scores"}
              </p>
            </div>
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            {/* Algorithm Badge */}
            <div className="mb-4">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                results.dataStructure === "hashtable"
                  ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                  : "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
              }`}>
                {results.dataStructure === "hashtable" ? "HashTable Algorithm" : "MinHeap Algorithm"}
              </span>
            </div>

            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
              Top 3 Recommendations for
            </h2>
            <p className="text-lg text-purple-600 dark:text-purple-400 mb-6">
              &quot;{results.searchedSong}&quot; by {results.searchedArtist}
            </p>

            <div className="space-y-4">
              {results.matches.map((match: any, index: number) => (
                <div
                  key={index}
                  className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6"
                >
                  <div className="flex items-center gap-4 mb-3">
                    {/* Rank Badge */}
                    <div className="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                      {index + 1}
                    </div>

                    {/* Song Info */}
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        {match.name}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {match.artist}
                      </p>
                    </div>

                    {/* Similarity Score */}
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {Math.round(match.similarity * 100)}%
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        Match
                      </div>
                    </div>
                  </div>

                  {/* Match bar */}
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${match.similarity * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}