"use client";

import { useState } from "react";

export default function Home() {
  const [songName, setSongName] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!songName.trim()) return;

    setIsSearching(true);

    // TODO: Replace this setTimeout with actual API call
    // Call your FastAPI backend at http://localhost:8000/recommend
    // Example:
    // try {
    //   const response = await fetch('http://localhost:8000/recommend', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ song_name: songName, top_k: 3 })
    //   });
    //   const data = await response.json();
    //   setResults(data);
    // } catch (error) {
    //   console.error('Error:', error);
    //   alert('Could not find song or connect to server');
    // } finally {
    //   setIsSearching(false);
    // }

    // Fake data for now
    setTimeout(() => {
      setResults({
        searchedSong: songName,
        matches: [
          {
            name: "Shape of You",
            artist: "Ed Sheeran",
            similarity: 0.92,
          },
          {
            name: "Levitating",
            artist: "Dua Lipa",
            similarity: 0.88,
          },
          {
            name: "Starboy",
            artist: "The Weeknd",
            similarity: 0.85,
          },
        ],
      });
      setIsSearching(false);
    }, 800);
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
            Find similar songs instantly
          </p>
        </div>

        {/* Search Box */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
          <form onSubmit={handleSearch}>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter a song name
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={songName}
                onChange={(e) => setSongName(e.target.value)}
                placeholder="e.g., Blinding Lights"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                disabled={isSearching}
              />
              <button
                type="submit"
                disabled={isSearching || !songName.trim()}
                className="px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-6">
              Top 3 Recommendations for "{results.searchedSong}"
            </h2>

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