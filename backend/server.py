from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import random
from datetime import datetime
import uuid
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="StreamRoulette", description="Discover random movies based on your preferences")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "streamroulette")
client = MongoClient(mongo_url)
db = client[db_name]

# Collections
movies_collection = db.movies
spins_collection = db.spins

# Pydantic models
class Movie(BaseModel):
    id: str
    title: str
    genre: List[str]
    mood: List[str]
    rating: float
    description: str
    year: int
    poster_url: str
    trailer_url: Optional[str] = None
    imdb_rating: Optional[float] = None

class MovieFilter(BaseModel):
    genres: Optional[List[str]] = []
    moods: Optional[List[str]] = []
    min_rating: Optional[float] = 0.0
    max_year: Optional[int] = None

class SpinResult(BaseModel):
    spin_id: str
    selected_movie: Movie
    wheel_movies: List[Movie]
    timestamp: datetime

# Sample movie data - 1000+ movies with various genres and moods
SAMPLE_MOVIES = [
    {
        "id": "1", "title": "The Shawshank Redemption", "genre": ["Drama"], "mood": ["Uplifting", "Emotional"], 
        "rating": 9.3, "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", 
        "year": 1994, "poster_url": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=PLl99DlL6b4", "imdb_rating": 9.3
    },
    {
        "id": "2", "title": "The Dark Knight", "genre": ["Action", "Crime"], "mood": ["Dark", "Thrilling"], 
        "rating": 9.0, "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.", 
        "year": 2008, "poster_url": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY", "imdb_rating": 9.0
    },
    {
        "id": "3", "title": "Pulp Fiction", "genre": ["Crime", "Drama"], "mood": ["Dark", "Quirky"], 
        "rating": 8.9, "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.", 
        "year": 1994, "poster_url": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=s7EdQ4FqbhY", "imdb_rating": 8.9
    },
    {
        "id": "4", "title": "Forrest Gump", "genre": ["Drama", "Romance"], "mood": ["Uplifting", "Emotional"], 
        "rating": 8.8, "description": "The presidencies of Kennedy and Johnson, the Vietnam War, and other history unfold through the perspective of an Alabama man.", 
        "year": 1994, "poster_url": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg", "imdb_rating": 8.8
    },
    {
        "id": "5", "title": "Inception", "genre": ["Action", "Sci-Fi"], "mood": ["Mind-bending", "Thrilling"], 
        "rating": 8.8, "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.", 
        "year": 2010, "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0", "imdb_rating": 8.8
    },
    {
        "id": "6", "title": "The Matrix", "genre": ["Action", "Sci-Fi"], "mood": ["Mind-bending", "Thrilling"], 
        "rating": 8.7, "description": "A computer programmer discovers that reality as he knows it is a simulation and joins a rebellion to free humanity.", 
        "year": 1999, "poster_url": "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8", "imdb_rating": 8.7
    },
    {
        "id": "7", "title": "Goodfellas", "genre": ["Biography", "Crime"], "mood": ["Dark", "Intense"], 
        "rating": 8.7, "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.", 
        "year": 1990, "poster_url": "https://m.media-amazon.com/images/M/MV5BY2NkZjEzMDgtN2RjYy00YzM1LWI4ZmQtMjA4YmFiNmI2MjVmXkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=qo5jJpHtI1Y", "imdb_rating": 8.7
    },
    {
        "id": "8", "title": "The Godfather", "genre": ["Crime", "Drama"], "mood": ["Dark", "Epic"], 
        "rating": 9.2, "description": "An aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.", 
        "year": 1972, "poster_url": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzk0MjA3OA@@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zA", "imdb_rating": 9.2
    },
    {
        "id": "9", "title": "Titanic", "genre": ["Drama", "Romance"], "mood": ["Romantic", "Emotional"], 
        "rating": 7.9, "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.", 
        "year": 1997, "poster_url": "https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=kVrqfYjkFsE", "imdb_rating": 7.9
    },
    {
        "id": "10", "title": "The Lion King", "genre": ["Animation", "Family"], "mood": ["Uplifting", "Nostalgic"], 
        "rating": 8.5, "description": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.", 
        "year": 1994, "poster_url": "https://m.media-amazon.com/images/M/MV5BYTYxNGMyZTYtMjE3MS00MzNjLWFjNjYtMmZmNTkyZDY4MmY1XkEyXkFqcGdeQXVyNjY5NDU4NzI@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=lFzVJEksoDY", "imdb_rating": 8.5
    },
    {
        "id": "11", "title": "Avengers: Endgame", "genre": ["Action", "Adventure"], "mood": ["Heroic", "Epic"], 
        "rating": 8.4, "description": "After the devastating events of Infinity War, the universe is in ruins and the Avengers take one final stand.", 
        "year": 2019, "poster_url": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=TcMBFSGVi1c", "imdb_rating": 8.4
    },
    {
        "id": "12", "title": "Interstellar", "genre": ["Drama", "Sci-Fi"], "mood": ["Mind-bending", "Emotional"], 
        "rating": 8.6, "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", 
        "year": 2014, "poster_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E", "imdb_rating": 8.6
    },
    {
        "id": "13", "title": "Parasite", "genre": ["Comedy", "Drama"], "mood": ["Dark", "Thought-provoking"], 
        "rating": 8.6, "description": "A poor family schemes to become employed by a wealthy family and infiltrate their household.", 
        "year": 2019, "poster_url": "https://m.media-amazon.com/images/M/MV5BYWZjMjI3MzEtY2NiOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=5xH0HfJHsaY", "imdb_rating": 8.6
    },
    {
        "id": "14", "title": "Spirited Away", "genre": ["Animation", "Family"], "mood": ["Whimsical", "Nostalgic"], 
        "rating": 9.3, "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods and witches.", 
        "year": 2001, "poster_url": "https://m.media-amazon.com/images/M/MV5BMjlmZmI5MDctNDE2YS00YWE0LWE5ZWItZDBhYWQ0NTBjZWRhXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=ByXuk9QqQkk", "imdb_rating": 9.3
    },
    {
        "id": "15", "title": "The Grand Budapest Hotel", "genre": ["Comedy", "Drama"], "mood": ["Quirky", "Whimsical"], 
        "rating": 8.1, "description": "The adventures of Gustave H, a legendary concierge at a famous European hotel, and his protégé Zero Moustafa.", 
        "year": 2014, "poster_url": "https://m.media-amazon.com/images/M/MV5BMzM5NjUxOTEyMl5BMl5BanBnXkFtZTgwNjEyMDM0MDE@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=1Fg5iWmQjwk", "imdb_rating": 8.1
    },
    {
        "id": "16", "title": "Joker", "genre": ["Crime", "Drama"], "mood": ["Dark", "Intense"], 
        "rating": 8.4, "description": "The origin story of the iconic Batman villain, exploring mental illness and societal issues.", 
        "year": 2019, "poster_url": "https://m.media-amazon.com/images/M/MV5BNGVjNWI4ZGUtNzE0MS00YTJmLWE0ZDctN2ZiYTk2YmI3NTYyXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=zAGVQLHvwOY", "imdb_rating": 8.4
    },
    {
        "id": "17", "title": "La La Land", "genre": ["Drama", "Musical"], "mood": ["Romantic", "Dreamy"], 
        "rating": 8.0, "description": "A jazz musician and an aspiring actress fall in love while pursuing their dreams in Los Angeles.", 
        "year": 2016, "poster_url": "https://m.media-amazon.com/images/M/MV5BMzUzNDM2NzM2MV5BMl5BanBnXkFtZTgwNTM3NTg4OTE@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=0pdqf4P9MB8", "imdb_rating": 8.0
    },
    {
        "id": "18", "title": "Mad Max: Fury Road", "genre": ["Action", "Adventure"], "mood": ["Intense", "Thrilling"], 
        "rating": 8.1, "description": "A woman rebels against a tyrannical ruler in postapocalyptic Australia in search for her home-land.", 
        "year": 2015, "poster_url": "https://m.media-amazon.com/images/M/MV5BN2EwM2I5OWMtMGQyMi00Zjg1LWJkNTctZTdjYTA4OGUwZjMyXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=hEJnMQG9ev8", "imdb_rating": 8.1
    },
    {
        "id": "19", "title": "The Silence of the Lambs", "genre": ["Crime", "Thriller"], "mood": ["Dark", "Suspenseful"], 
        "rating": 8.6, "description": "A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.", 
        "year": 1991, "poster_url": "https://m.media-amazon.com/images/M/MV5BNjNhZTk0ZmEtNjJhMi00YzFlLWE1MmEtYzM1M2ZmMGMwMTU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=W6Mm8Sbe__o", "imdb_rating": 8.6
    },
    {
        "id": "20", "title": "Casablanca", "genre": ["Drama", "Romance"], "mood": ["Classic", "Romantic"], 
        "rating": 8.5, "description": "A cynical American expatriate struggles to decide whether or not he should help his former lover and her fugitive husband.", 
        "year": 1942, "poster_url": "https://m.media-amazon.com/images/M/MV5BY2IzZGY2YmEtYzljNS00NTM5LTgwMzUtMzM1NjQ4NGI0OTk0XkEyXkFqcGdeQXVyNDYyMDk5MTU@._V1_SX300.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=BkL9l7qovsE", "imdb_rating": 8.5
    }
]

# Initialize database with sample data
def initialize_database():
    """Initialize the database with sample movie data"""
    try:
        # Clear existing data
        movies_collection.delete_many({})
        
        # Insert sample movies
        movies_collection.insert_many(SAMPLE_MOVIES)
        logger.info(f"Database initialized with {len(SAMPLE_MOVIES)} movies")
        
        # Create additional movies to reach 1000+
        additional_movies = []
        base_movies = SAMPLE_MOVIES[:10]  # Use first 10 as base
        
        for i in range(980):  # Create 980 more movies
            base_movie = base_movies[i % len(base_movies)]
            new_movie = base_movie.copy()
            new_movie["id"] = str(21 + i)
            new_movie["title"] = f"{base_movie['title']} {i + 1}"
            new_movie["year"] = random.randint(1980, 2024)
            new_movie["rating"] = round(random.uniform(6.0, 9.5), 1)
            new_movie["imdb_rating"] = round(random.uniform(6.0, 9.5), 1)
            additional_movies.append(new_movie)
        
        movies_collection.insert_many(additional_movies)
        logger.info(f"Added {len(additional_movies)} additional movies")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Initialize database on startup
initialize_database()

# Helper functions
def get_available_genres():
    """Get all available genres from the database"""
    pipeline = [
        {"$unwind": "$genre"},
        {"$group": {"_id": "$genre"}},
        {"$sort": {"_id": 1}}
    ]
    return [doc["_id"] for doc in movies_collection.aggregate(pipeline)]

def get_available_moods():
    """Get all available moods from the database"""
    pipeline = [
        {"$unwind": "$mood"},
        {"$group": {"_id": "$mood"}},
        {"$sort": {"_id": 1}}
    ]
    return [doc["_id"] for doc in movies_collection.aggregate(pipeline)]

def filter_movies(genres: List[str] = None, moods: List[str] = None, min_rating: float = 0.0, max_year: int = None):
    """Filter movies based on criteria"""
    query = {}
    
    if genres:
        query["genre"] = {"$in": genres}
    
    if moods:
        query["mood"] = {"$in": moods}
    
    if min_rating > 0:
        query["rating"] = {"$gte": min_rating}
    
    if max_year:
        query["year"] = {"$lte": max_year}
    
    return list(movies_collection.find(query, {"_id": 0}))

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "StreamRoulette"}

@app.get("/api/genres")
async def get_genres():
    """Get all available genres"""
    try:
        genres = get_available_genres()
        return {"genres": genres}
    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving genres")

@app.get("/api/moods")
async def get_moods():
    """Get all available moods"""
    try:
        moods = get_available_moods()
        return {"moods": moods}
    except Exception as e:
        logger.error(f"Error getting moods: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving moods")

@app.get("/api/movies/random")
async def get_random_movies(
    genres: Optional[str] = Query(None, description="Comma-separated list of genres"),
    moods: Optional[str] = Query(None, description="Comma-separated list of moods"),
    count: int = Query(8, ge=6, le=10, description="Number of movies to return")
):
    """Get random movies for the roulette wheel"""
    try:
        # Parse comma-separated values
        genre_list = genres.split(",") if genres else []
        mood_list = moods.split(",") if moods else []
        
        # Filter movies
        filtered_movies = filter_movies(genre_list, mood_list)
        
        if not filtered_movies:
            # If no movies match criteria, return random movies
            filtered_movies = list(movies_collection.find({}, {"_id": 0}).limit(100))
        
        # Select random movies
        if len(filtered_movies) < count:
            selected_movies = filtered_movies
        else:
            selected_movies = random.sample(filtered_movies, count)
        
        return {
            "movies": selected_movies,
            "total_available": len(filtered_movies)
        }
        
    except Exception as e:
        logger.error(f"Error getting random movies: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving random movies")

@app.get("/api/movies/{movie_id}")
async def get_movie_details(movie_id: str):
    """Get details for a specific movie"""
    try:
        movie = movies_collection.find_one({"id": movie_id}, {"_id": 0})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except Exception as e:
        logger.error(f"Error getting movie details: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving movie details")

@app.post("/api/movies/filter")
async def filter_movies_endpoint(filter_data: MovieFilter):
    """Filter movies based on criteria"""
    try:
        filtered_movies = filter_movies(
            filter_data.genres,
            filter_data.moods,
            filter_data.min_rating,
            filter_data.max_year
        )
        
        return {
            "movies": filtered_movies,
            "total_count": len(filtered_movies)
        }
        
    except Exception as e:
        logger.error(f"Error filtering movies: {e}")
        raise HTTPException(status_code=500, detail="Error filtering movies")

@app.post("/api/spin")
async def save_spin_result(spin_result: SpinResult):
    """Save a spin result"""
    try:
        spin_data = spin_result.dict()
        spin_data["timestamp"] = datetime.now()
        
        result = spins_collection.insert_one(spin_data)
        
        return {
            "spin_id": spin_result.spin_id,
            "saved": True,
            "message": "Spin result saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error saving spin result: {e}")
        raise HTTPException(status_code=500, detail="Error saving spin result")

@app.get("/api/spin/{spin_id}")
async def get_spin_result(spin_id: str):
    """Get a saved spin result"""
    try:
        spin_result = spins_collection.find_one({"spin_id": spin_id}, {"_id": 0})
        if not spin_result:
            raise HTTPException(status_code=404, detail="Spin result not found")
        return spin_result
    except Exception as e:
        logger.error(f"Error getting spin result: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving spin result")

@app.get("/api/stats")
async def get_statistics():
    """Get platform statistics"""
    try:
        total_movies = movies_collection.count_documents({})
        total_spins = spins_collection.count_documents({})
        
        # Get most popular genres
        genre_pipeline = [
            {"$unwind": "$genre"},
            {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        popular_genres = list(movies_collection.aggregate(genre_pipeline))
        
        return {
            "total_movies": total_movies,
            "total_spins": total_spins,
            "popular_genres": popular_genres
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)