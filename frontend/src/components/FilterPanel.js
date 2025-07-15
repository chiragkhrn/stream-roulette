import React from 'react';
import { motion } from 'framer-motion';
import { Filter, RotateCw, X } from 'lucide-react';

const FilterPanel = ({ 
  genres, 
  moods, 
  selectedGenres, 
  selectedMoods, 
  onGenreChange, 
  onMoodChange, 
  onReset 
}) => {
  const handleGenreToggle = (genre) => {
    if (selectedGenres.includes(genre)) {
      onGenreChange(selectedGenres.filter(g => g !== genre));
    } else {
      onGenreChange([...selectedGenres, genre]);
    }
  };

  const handleMoodToggle = (mood) => {
    if (selectedMoods.includes(mood)) {
      onMoodChange(selectedMoods.filter(m => m !== mood));
    } else {
      onMoodChange([...selectedMoods, mood]);
    }
  };

  const clearFilters = () => {
    onGenreChange([]);
    onMoodChange([]);
  };

  const hasFilters = selectedGenres.length > 0 || selectedMoods.length > 0;

  return (
    <motion.div
      className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8 border border-white/20"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Filter className="w-6 h-6 text-blue-300" />
          <h2 className="text-2xl font-bold text-white">Filter Your Perfect Movie</h2>
        </div>
        
        {hasFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center space-x-2 px-4 py-2 bg-red-500/20 text-red-200 rounded-lg hover:bg-red-500/30 transition-colors"
          >
            <X className="w-4 h-4" />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {/* Genres */}
      <div className="mb-6">
        <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
          <span>🎭</span>
          <span>Genres</span>
          {selectedGenres.length > 0 && (
            <span className="text-blue-300 text-sm">({selectedGenres.length} selected)</span>
          )}
        </h3>
        <div className="flex flex-wrap gap-2">
          {genres.map((genre) => (
            <motion.button
              key={genre}
              onClick={() => handleGenreToggle(genre)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                selectedGenres.includes(genre)
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                  : 'bg-white/10 text-blue-100 hover:bg-white/20'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {genre}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Moods */}
      <div>
        <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
          <span>🎭</span>
          <span>Moods</span>
          {selectedMoods.length > 0 && (
            <span className="text-blue-300 text-sm">({selectedMoods.length} selected)</span>
          )}
        </h3>
        <div className="flex flex-wrap gap-2">
          {moods.map((mood) => (
            <motion.button
              key={mood}
              onClick={() => handleMoodToggle(mood)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                selectedMoods.includes(mood)
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg'
                  : 'bg-white/10 text-blue-100 hover:bg-white/20'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {mood}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasFilters && (
        <motion.div
          className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <h4 className="text-white font-semibold mb-2">Active Filters:</h4>
          <div className="flex flex-wrap gap-2">
            {selectedGenres.map((genre) => (
              <span
                key={`genre-${genre}`}
                className="px-3 py-1 bg-purple-500/30 text-purple-200 rounded-full text-sm border border-purple-400/30"
              >
                {genre}
              </span>
            ))}
            {selectedMoods.map((mood) => (
              <span
                key={`mood-${mood}`}
                className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-full text-sm border border-blue-400/30"
              >
                {mood}
              </span>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default FilterPanel;