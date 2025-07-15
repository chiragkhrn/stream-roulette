import React from 'react';
import { motion } from 'framer-motion';
import { Share2, RotateCw, Star, Calendar, PlayCircle, Heart } from 'lucide-react';

const MovieCard = ({ movie, onShare, onSpinAgain }) => {
  const handleWatchTrailer = () => {
    if (movie.trailer_url) {
      window.open(movie.trailer_url, '_blank');
    }
  };

  const getRatingColor = (rating) => {
    if (rating >= 8.5) return 'text-green-400';
    if (rating >= 7.5) return 'text-yellow-400';
    if (rating >= 6.5) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <motion.div
      className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20"
      initial={{ opacity: 0, scale: 0.8, y: 50 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
    >
      {/* Header */}
      <motion.div
        className="text-center mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <h2 className="text-3xl font-bold text-white mb-2">🎉 Your Movie Pick! 🎉</h2>
        <p className="text-blue-200">The wheel has spoken...</p>
      </motion.div>

      {/* Movie Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Movie Poster */}
        <motion.div
          className="flex justify-center"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <div className="relative group">
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="w-full max-w-sm rounded-xl shadow-2xl transform group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                e.target.src = `https://via.placeholder.com/300x450/4F46E5/FFFFFF?text=${encodeURIComponent(movie.title)}`;
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
        </motion.div>

        {/* Movie Details */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          {/* Title */}
          <div>
            <h3 className="text-4xl font-bold text-white mb-2">{movie.title}</h3>
            <div className="flex items-center space-x-4 text-blue-200">
              <div className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>{movie.year}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Star className={`w-4 h-4 ${getRatingColor(movie.rating)}`} />
                <span className={getRatingColor(movie.rating)}>{movie.rating}/10</span>
              </div>
            </div>
          </div>

          {/* Genres */}
          <div>
            <h4 className="text-white font-semibold mb-2">Genres</h4>
            <div className="flex flex-wrap gap-2">
              {movie.genre.map((genre, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gradient-to-r from-purple-500/30 to-pink-500/30 text-white rounded-full text-sm border border-purple-400/30"
                >
                  {genre}
                </span>
              ))}
            </div>
          </div>

          {/* Moods */}
          <div>
            <h4 className="text-white font-semibold mb-2">Mood</h4>
            <div className="flex flex-wrap gap-2">
              {movie.mood.map((mood, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gradient-to-r from-blue-500/30 to-cyan-500/30 text-white rounded-full text-sm border border-blue-400/30"
                >
                  {mood}
                </span>
              ))}
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 className="text-white font-semibold mb-2">Description</h4>
            <p className="text-blue-100 leading-relaxed">{movie.description}</p>
          </div>

          {/* IMDb Rating */}
          {movie.imdb_rating && (
            <div className="flex items-center space-x-2">
              <span className="text-yellow-400 font-semibold">IMDb:</span>
              <div className="flex items-center space-x-1">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <span className="text-yellow-400 font-bold">{movie.imdb_rating}/10</span>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Action Buttons */}
      <motion.div
        className="flex flex-col sm:flex-row gap-4 mt-8 pt-8 border-t border-white/20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <button
          onClick={handleWatchTrailer}
          className="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-red-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2"
        >
          <PlayCircle className="w-5 h-5" />
          <span>Watch Trailer</span>
        </button>
        
        <button
          onClick={onShare}
          className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2"
        >
          <Share2 className="w-5 h-5" />
          <span>Share Result</span>
        </button>
        
        <button
          onClick={onSpinAgain}
          className="flex-1 bg-gradient-to-r from-purple-500 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2"
        >
          <RotateCw className="w-5 h-5" />
          <span>Spin Again</span>
        </button>
      </motion.div>

      {/* Fun Stats */}
      <motion.div
        className="mt-6 p-4 bg-white/5 rounded-lg"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.5 }}
      >
        <div className="flex items-center justify-center space-x-6 text-blue-200">
          <div className="flex items-center space-x-1">
            <Heart className="w-4 h-4" />
            <span className="text-sm">Added to your watchlist</span>
          </div>
          <div className="flex items-center space-x-1">
            <Star className="w-4 h-4" />
            <span className="text-sm">Perfect match found!</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MovieCard;