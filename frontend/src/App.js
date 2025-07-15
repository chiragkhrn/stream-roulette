import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Share2, RotateCw, Star, Calendar, Film, Heart, Trophy, Sparkles } from 'lucide-react';
import RouletteWheel from './components/RouletteWheel';
import MovieCard from './components/MovieCard';
import FilterPanel from './components/FilterPanel';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [genres, setGenres] = useState([]);
  const [moods, setMoods] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedMoods, setSelectedMoods] = useState([]);
  const [wheelMovies, setWheelMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [spinCount, setSpinCount] = useState(0);
  const [stats, setStats] = useState({});

  useEffect(() => {
    loadInitialData();
    loadStats();
    loadLastResult();
  }, []);

  const loadInitialData = async () => {
    try {
      const [genresRes, moodsRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/genres`),
        fetch(`${BACKEND_URL}/api/moods`)
      ]);
      
      const genresData = await genresRes.json();
      const moodsData = await moodsRes.json();
      
      setGenres(genresData.genres);
      setMoods(moodsData.moods);
    } catch (err) {
      setError('Failed to load initial data');
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadLastResult = () => {
    const saved = localStorage.getItem('streamroulette_last_result');
    if (saved) {
      try {
        const result = JSON.parse(saved);
        setSelectedMovie(result.selectedMovie);
        setWheelMovies(result.wheelMovies);
        setShowResult(true);
      } catch (err) {
        localStorage.removeItem('streamroulette_last_result');
      }
    }
  };

  const handleSpin = async () => {
    if (isSpinning || isLoading) return;
    
    setIsLoading(true);
    setError('');
    setShowResult(false);
    setSelectedMovie(null);
    
    try {
      const genreParam = selectedGenres.length > 0 ? selectedGenres.join(',') : '';
      const moodParam = selectedMoods.length > 0 ? selectedMoods.join(',') : '';
      
      const response = await fetch(
        `${BACKEND_URL}/api/movies/random?genres=${genreParam}&moods=${moodParam}&count=8`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch movies');
      }
      
      const data = await response.json();
      
      if (data.movies.length === 0) {
        setError('No movies found matching your criteria. Try different filters.');
        setIsLoading(false);
        return;
      }
      
      setWheelMovies(data.movies);
      setIsSpinning(true);
      setIsLoading(false);
      
    } catch (err) {
      setError(`Error: ${err.message}`);
      setIsLoading(false);
    }
  };

  const handleSpinComplete = (selectedMovie) => {
    setSelectedMovie(selectedMovie);
    setIsSpinning(false);
    setShowResult(true);
    setSpinCount(prev => prev + 1);
    
    // Save to localStorage
    const result = {
      selectedMovie,
      wheelMovies,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('streamroulette_last_result', JSON.stringify(result));
  };

  const handleShare = () => {
    if (!selectedMovie) return;
    
    const shareText = `🎬 StreamRoulette picked "${selectedMovie.title}" (${selectedMovie.year}) for me! ⭐ ${selectedMovie.rating}/10\n\n${selectedMovie.description}\n\nTry it yourself at StreamRoulette!`;
    
    if (navigator.share) {
      navigator.share({
        title: 'StreamRoulette Result',
        text: shareText,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(shareText);
      alert('Result copied to clipboard!');
    }
  };

  const resetSpin = () => {
    setShowResult(false);
    setSelectedMovie(null);
    setWheelMovies([]);
    setIsSpinning(false);
    localStorage.removeItem('streamroulette_last_result');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Background Animation */}
      <div className="fixed inset-0 overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-20"
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear'
          }}
          style={{
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%)',
            backgroundSize: '400% 400%'
          }}
        />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <motion.header 
          className="text-center py-12 px-4"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-block"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <h1 className="text-6xl md:text-8xl font-bold text-white mb-4 bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
              StreamRoulette
            </h1>
          </motion.div>
          <motion.p 
            className="text-xl md:text-2xl text-blue-100 mb-2 max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            Spin the wheel and discover your next favorite movie!
          </motion.p>
          <motion.p 
            className="text-lg text-blue-200 max-w-xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            Select your preferences and let fate decide what you watch tonight
          </motion.p>
          
          {/* Stats */}
          {stats.total_movies && (
            <motion.div 
              className="flex justify-center items-center space-x-6 mt-6 text-blue-200"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
            >
              <div className="flex items-center space-x-2">
                <Film className="w-5 h-5" />
                <span>{stats.total_movies}+ Movies</span>
              </div>
              <div className="flex items-center space-x-2">
                <Trophy className="w-5 h-5" />
                <span>{stats.total_spins || 0} Spins</span>
              </div>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5" />
                <span>{spinCount} Your Spins</span>
              </div>
            </motion.div>
          )}
        </motion.header>

        {/* Main Content */}
        <div className="container mx-auto px-4 pb-12">
          <div className="max-w-6xl mx-auto">
            
            {/* Filter Panel */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <FilterPanel
                genres={genres}
                moods={moods}
                selectedGenres={selectedGenres}
                selectedMoods={selectedMoods}
                onGenreChange={setSelectedGenres}
                onMoodChange={setSelectedMoods}
                onReset={resetSpin}
              />
            </motion.div>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  className="max-w-md mx-auto mb-8 p-4 bg-red-500/20 border border-red-500/50 rounded-lg"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.3 }}
                >
                  <p className="text-red-200 text-center">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Roulette Wheel */}
            <motion.div
              className="flex justify-center mb-12"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, duration: 0.6 }}
            >
              <RouletteWheel
                movies={wheelMovies}
                isSpinning={isSpinning}
                onSpinComplete={handleSpinComplete}
                isLoading={isLoading}
              />
            </motion.div>

            {/* Spin Button */}
            <motion.div
              className="flex justify-center mb-12"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <motion.button
                onClick={handleSpin}
                disabled={isSpinning || isLoading}
                className={`px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 ${
                  isSpinning || isLoading
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 transform hover:scale-105'
                } text-white shadow-lg`}
                whileHover={{ scale: isSpinning || isLoading ? 1 : 1.05 }}
                whileTap={{ scale: isSpinning || isLoading ? 1 : 0.95 }}
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Finding Movies...</span>
                  </div>
                ) : isSpinning ? (
                  <div className="flex items-center space-x-2">
                    <RotateCw className="w-5 h-5 animate-spin" />
                    <span>Spinning...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Play className="w-5 h-5" />
                    <span>Spin the Wheel!</span>
                  </div>
                )}
              </motion.button>
            </motion.div>

            {/* Movie Result */}
            <AnimatePresence>
              {showResult && selectedMovie && (
                <motion.div
                  className="max-w-4xl mx-auto"
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -50 }}
                  transition={{ duration: 0.6 }}
                >
                  <MovieCard 
                    movie={selectedMovie} 
                    onShare={handleShare}
                    onSpinAgain={resetSpin}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;