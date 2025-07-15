import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const RouletteWheel = ({ movies, isSpinning, onSpinComplete, isLoading }) => {
  const [rotation, setRotation] = useState(0);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wheelRef = useRef(null);

  useEffect(() => {
    if (isSpinning && movies.length > 0) {
      spinWheel();
    }
  }, [isSpinning, movies]);

  const spinWheel = () => {
    // Calculate winning index
    const winningIndex = Math.floor(Math.random() * movies.length);
    setSelectedIndex(winningIndex);
    
    // Calculate rotation needed to land on winning segment
    const segmentAngle = 360 / movies.length;
    const targetAngle = -(winningIndex * segmentAngle) + (segmentAngle / 2);
    
    // Add multiple full rotations for dramatic effect
    const spins = 5 + Math.random() * 3; // 5-8 full rotations
    const finalRotation = rotation + (spins * 360) + targetAngle;
    
    setRotation(finalRotation);
    
    // Call onSpinComplete after animation
    setTimeout(() => {
      onSpinComplete(movies[winningIndex]);
    }, 4000);
  };

  const getColor = (index) => {
    const colors = [
      'from-red-500 to-red-600',
      'from-blue-500 to-blue-600',
      'from-green-500 to-green-600',
      'from-purple-500 to-purple-600',
      'from-yellow-500 to-yellow-600',
      'from-pink-500 to-pink-600',
      'from-indigo-500 to-indigo-600',
      'from-orange-500 to-orange-600'
    ];
    return colors[index % colors.length];
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center w-80 h-80 bg-white/10 rounded-full backdrop-blur-sm">
        <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-white text-lg">Loading movies...</p>
      </div>
    );
  }

  if (movies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center w-80 h-80 bg-white/10 rounded-full backdrop-blur-sm">
        <div className="text-6xl mb-4">🎬</div>
        <p className="text-white text-lg text-center">
          Select your preferences and<br />click "Spin the Wheel!"
        </p>
      </div>
    );
  }

  const segmentAngle = 360 / movies.length;

  return (
    <div className="relative">
      {/* Wheel Container */}
      <div className="relative w-80 h-80">
        {/* Wheel */}
        <motion.div
          ref={wheelRef}
          className="w-full h-full rounded-full relative overflow-hidden shadow-2xl"
          style={{
            background: 'conic-gradient(from 0deg, #4F46E5, #7C3AED, #EC4899, #EF4444, #F59E0B, #10B981, #06B6D4, #4F46E5)'
          }}
          animate={{ rotate: rotation }}
          transition={{
            duration: 4,
            ease: [0.23, 1, 0.320, 1],
            type: "tween"
          }}
        >
          {/* Segments */}
          {movies.map((movie, index) => {
            const angle = index * segmentAngle;
            const nextAngle = (index + 1) * segmentAngle;
            
            return (
              <div
                key={movie.id}
                className="absolute w-full h-full flex items-center justify-center"
                style={{
                  clipPath: `polygon(50% 50%, ${50 + 50 * Math.cos((angle - 90) * Math.PI / 180)}% ${50 + 50 * Math.sin((angle - 90) * Math.PI / 180)}%, ${50 + 50 * Math.cos((nextAngle - 90) * Math.PI / 180)}% ${50 + 50 * Math.sin((nextAngle - 90) * Math.PI / 180)}%)`,
                  transform: `rotate(${angle + segmentAngle / 2}deg)`,
                  background: `linear-gradient(135deg, ${getColor(index).replace('from-', '').replace('to-', ', ')})`,
                }}
              >
                <div 
                  className="text-white font-bold text-sm text-center px-2 max-w-24"
                  style={{
                    transform: `rotate(${-(angle + segmentAngle / 2)}deg)`,
                    fontSize: movies.length > 6 ? '0.7rem' : '0.8rem'
                  }}
                >
                  {movie.title.length > 20 ? movie.title.substring(0, 17) + '...' : movie.title}
                </div>
              </div>
            );
          })}
          
          {/* Center Circle */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">🎬</span>
            </div>
          </div>
        </motion.div>
        
        {/* Pointer */}
        <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 z-10">
          <div className="w-0 h-0 border-l-4 border-r-4 border-b-8 border-l-transparent border-r-transparent border-b-white"></div>
        </div>
      </div>
      
      {/* Spinning Status */}
      {isSpinning && (
        <motion.div
          className="absolute -bottom-12 left-1/2 transform -translate-x-1/2"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-white text-lg font-semibold animate-pulse">
            🎲 Spinning... 🎲
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default RouletteWheel;