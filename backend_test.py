#!/usr/bin/env python3
"""
Backend API Testing for StreamRoulette Movie Discovery App
Tests all API endpoints using the public URL
"""

import requests
import json
import sys
from datetime import datetime
import time
import uuid

class StreamRouletteAPITester:
    def __init__(self, base_url="https://9b277e5b-c37b-4d0a-8c83-4617d52bead6.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.sample_movie_id = None
        self.sample_spin_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Service: {data.get('service')}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Health Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_get_genres(self):
        """Test get genres endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/genres", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                genres = data.get('genres', [])
                details = f"Found {len(genres)} genres: {genres[:5]}..."
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Genres", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Genres", False, str(e))
            return False

    def test_get_moods(self):
        """Test get moods endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/moods", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                moods = data.get('moods', [])
                details = f"Found {len(moods)} moods: {moods[:5]}..."
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Moods", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Moods", False, str(e))
            return False

    def test_get_random_movies(self):
        """Test get random movies endpoint"""
        try:
            # Test without filters
            response = requests.get(f"{self.base_url}/api/movies/random", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                movies = data.get('movies', [])
                total_available = data.get('total_available', 0)
                if movies:
                    self.sample_movie_id = movies[0]['id']
                details = f"Got {len(movies)} movies, {total_available} total available"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Random Movies (No Filter)", success, details)
            
            # Test with filters
            response2 = requests.get(f"{self.base_url}/api/movies/random?genres=Action,Drama&moods=Thrilling&count=6", timeout=15)
            success2 = response2.status_code == 200
            
            if success2:
                data2 = response2.json()
                movies2 = data2.get('movies', [])
                details2 = f"Filtered: Got {len(movies2)} movies with Action/Drama + Thrilling"
            else:
                details2 = f"Filtered request failed: {response2.status_code}"
                
            self.log_test("Get Random Movies (With Filters)", success2, details2)
            return success and success2
            
        except Exception as e:
            self.log_test("Get Random Movies", False, str(e))
            return False

    def test_get_movie_details(self):
        """Test get movie details endpoint"""
        if not self.sample_movie_id:
            self.log_test("Get Movie Details", False, "No sample movie ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/movies/{self.sample_movie_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                title = data.get('title', 'Unknown')
                rating = data.get('rating', 0)
                year = data.get('year', 0)
                details = f"Movie: {title} ({year}), Rating: {rating}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Movie Details", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Movie Details", False, str(e))
            return False

    def test_filter_movies(self):
        """Test filter movies endpoint"""
        try:
            payload = {
                "genres": ["Action", "Drama"],
                "moods": ["Thrilling"],
                "min_rating": 7.0,
                "max_year": 2020
            }
            
            response = requests.post(
                f"{self.base_url}/api/movies/filter",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                movies = data.get('movies', [])
                total_count = data.get('total_count', 0)
                details = f"Filtered {total_count} movies, returned {len(movies)}"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:100]}..."
                
            self.log_test("Filter Movies", success, details)
            return success
            
        except Exception as e:
            self.log_test("Filter Movies", False, str(e))
            return False

    def test_save_spin_result(self):
        """Test save spin result endpoint"""
        try:
            self.sample_spin_id = str(uuid.uuid4())
            
            # Create sample spin result
            payload = {
                "spin_id": self.sample_spin_id,
                "selected_movie": {
                    "id": "1",
                    "title": "Test Movie",
                    "genre": ["Action"],
                    "mood": ["Thrilling"],
                    "rating": 8.5,
                    "description": "Test movie description",
                    "year": 2023,
                    "poster_url": "https://example.com/poster.jpg",
                    "trailer_url": "https://example.com/trailer",
                    "imdb_rating": 8.5
                },
                "wheel_movies": [
                    {
                        "id": "1",
                        "title": "Test Movie",
                        "genre": ["Action"],
                        "mood": ["Thrilling"],
                        "rating": 8.5,
                        "description": "Test movie description",
                        "year": 2023,
                        "poster_url": "https://example.com/poster.jpg",
                        "trailer_url": "https://example.com/trailer",
                        "imdb_rating": 8.5
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/api/spin",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                spin_id = data.get('spin_id')
                saved = data.get('saved')
                details = f"Spin ID: {spin_id[:8]}..., Saved: {saved}"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:100]}..."
                
            self.log_test("Save Spin Result", success, details)
            return success
            
        except Exception as e:
            self.log_test("Save Spin Result", False, str(e))
            return False

    def test_get_spin_result(self):
        """Test get spin result endpoint"""
        if not self.sample_spin_id:
            self.log_test("Get Spin Result", False, "No sample spin ID available")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/spin/{self.sample_spin_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                spin_id = data.get('spin_id')
                selected_movie = data.get('selected_movie', {})
                movie_title = selected_movie.get('title', 'Unknown')
                details = f"Spin ID: {spin_id[:8]}..., Movie: {movie_title}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Spin Result", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Spin Result", False, str(e))
            return False

    def test_get_statistics(self):
        """Test get statistics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                total_movies = data.get('total_movies', 0)
                total_spins = data.get('total_spins', 0)
                popular_genres = data.get('popular_genres', [])
                details = f"Movies: {total_movies}, Spins: {total_spins}, Top genres: {len(popular_genres)}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Statistics", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Statistics", False, str(e))
            return False

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        try:
            # Test invalid movie ID
            response = requests.get(f"{self.base_url}/api/movies/invalid_id_999", timeout=10)
            success = response.status_code == 404
            details = f"Invalid movie ID handled with status: {response.status_code}"
            
            self.log_test("Error Handling (Invalid Movie ID)", success, details)
            
            # Test invalid spin ID
            response2 = requests.get(f"{self.base_url}/api/spin/invalid_spin_id", timeout=10)
            success2 = response2.status_code == 404
            details2 = f"Invalid spin ID handled with status: {response2.status_code}"
            
            self.log_test("Error Handling (Invalid Spin ID)", success2, details2)
            return success and success2
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🎬 Starting StreamRoulette API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic endpoint tests
        self.test_health_check()
        self.test_get_genres()
        self.test_get_moods()
        self.test_get_statistics()
        
        # Core functionality tests
        self.test_get_random_movies()
        self.test_get_movie_details()
        self.test_filter_movies()
        
        # Spin functionality tests
        self.test_save_spin_result()
        self.test_get_spin_result()
        
        # Error handling tests
        self.test_error_handling()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    """Main test runner"""
    tester = StreamRouletteAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())