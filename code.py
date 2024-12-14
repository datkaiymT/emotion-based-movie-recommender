import os  # For interacting with the operating system (e.g., file operations)
import csv  # For reading and writing CSV/TSV files
import requests  # For making HTTP requests to fetch web pages
from bs4 import BeautifulSoup  # For parsing HTML content
from transformers import pipeline  # For loading pre-trained NLP models
from textblob import TextBlob  # For simple sentiment analysis
import sys  # For system-specific parameters and functions
import time  # For adding delays between requests to prevent overwhelming servers

emotion_classifier = pipeline(
    "text-classification",
    model="nateraw/bert-base-uncased-emotion",  # Pre-trained emotion classification model
    return_all_scores=True,  # Return scores for all possible labels
    truncation=True,  # Truncate texts that are too long for the model
    padding=True,  # Pad shorter texts to maintain consistent input size
    max_length=512  # Maximum token length for the model
)

WATCHED_FILE = "watched.txt"  # Stores watched movies along with reviews and status
PREFERENCES_FILE = "preferences.txt"  # Stores user preferences (genres, emotions, year)
WATCH_LATER_FILE = "watch_later.txt"  # Stores movies the user intends to watch later
FULL_TITLE_FILE = "full_title.basics.tsv"  # TSV file containing movie details
TITLE_RATINGS_FILE = "title.ratings.tsv"  # TSV file containing movie ratings and vote counts

# Function to display the main menu to the user
def display_main_menu():
    print("\nWelcome to Movie Match")
    print("1. Recommend a movie")
    print("2. View a watched list")
    print("3. View a watch later list")
    print("4. Search by title")
    print("5. Quit")

# Function to display the recommendation submenu
def display_recommendation_menu():
    print("\nRecommend a Movie")
    print("1. Recommend based on preferences")
    print("2. Renew preferences")
    print("3. Go back to menu")

# Function to read TSV (Tab-Separated Values) files and return a list of dictionaries
def read_tsv(file_path):
    data = []
    try:
        with open(file_path, encoding='utf-8') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')  # Initialize TSV reader
            for row in reader:
                data.append(row)  # Append each row as a dictionary to the data list
    except FileNotFoundError:
        print(f"File {file_path} not found.")  # Inform the user if the file doesn't exist
    return data  # Return the list of movie data

# Function to read the watched list from 'watched.txt'
def read_watched():
    watched = []
    if os.path.exists(WATCHED_FILE):  # Check if the watched file exists
        with open(WATCHED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()  # Remove leading/trailing whitespace
                if line:
                    parts = line.split(':')  # Split the line into title, review, and status
                    if len(parts) == 3:
                        number_title = parts[0].split('.', 1)  # Separate the number from the title
                        if len(number_title) == 2:
                            watched.append({
                                'number': number_title[0],  # The numbering of the movie in the list
                                'title': number_title[1],   # The movie title
                                'review': parts[1],         # The user's review of the movie
                                'status': parts[2]          # The sentiment status ('like'/'dislike')
                            })
    return watched  # Return the list of watched movies

# Function to read the watch later list from 'watch_later.txt'
def read_watch_later():
    watch_later = []
    if os.path.exists(WATCH_LATER_FILE):  # Check if the watch later file exists
        with open(WATCH_LATER_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()  # Read the entire content and strip whitespace
            if content:
                # Split the content by commas and strip each title
                watch_later = [title.strip() for title in content.split(',') if title.strip()]
    return watch_later  # Return the list of watch later movies

# Function to read user preferences from 'preferences.txt'
def read_preferences():
    preferences = {
        'Genres': [],    # List of preferred genres
        'Emotions': [],  # List of preferred emotions
        'Year': ''       # Preferred year category
    }
    if os.path.exists(PREFERENCES_FILE):  # Check if the preferences file exists
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Genres:"):
                    genres = line.replace("Genres:", "").strip()
                    # Split genres by comma and strip whitespace
                    preferences['Genres'] = [genre.strip() for genre in genres.split(',') if genre.strip()]
                elif line.startswith("Emotions:"):
                    emotions = line.replace("Emotions:", "").strip()
                    # Split emotions by comma and strip whitespace
                    preferences['Emotions'] = [emotion.strip() for emotion in emotions.split(',') if emotion.strip()]
                elif line.startswith("Year:"):
                    preferences['Year'] = line.replace("Year:", "").strip()  # Extract year category
    return preferences  # Return the dictionary of preferences

# Function to write user preferences to 'preferences.txt'
def write_preferences(preferences):
    with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
        # Write genres, emotions, and year preferences separated by commas
        f.write(f"Genres:{','.join(preferences['Genres'])}\n")
        f.write(f"Emotions:{','.join(preferences['Emotions'])}\n")
        f.write(f"Year:{preferences['Year']}\n")

# Function to append a movie to the watched list
def append_watched(title, review, status):
    watched = read_watched()  # Read the current watched list
    number = len(watched) + 1  # Determine the next number in the list
    with open(WATCHED_FILE, 'a', encoding='utf-8') as f:
        # Write the movie details in the format: number.title:review:status
        f.write(f"{number}.{title}:{review}:{status}\n")

# Function to append a movie to the watch later list
def append_watch_later(title):
    watch_later = read_watch_later()  # Read the current watch later list
    watch_later.append(title)  # Add the new title
    with open(WATCH_LATER_FILE, 'w', encoding='utf-8') as f:
        # Write all watch later titles separated by commas
        f.write(','.join(watch_later))

# Function to remove a movie from the watch later list by index
def remove_watch_later(index):
    watch_later = read_watch_later()  # Read the current watch later list
    if 0 <= index < len(watch_later):  # Check if the index is valid
        removed = watch_later.pop(index)  # Remove the movie at the specified index
        with open(WATCH_LATER_FILE, 'w', encoding='utf-8') as f:
            # Write the updated list back to the file
            f.write(','.join(watch_later))
        return removed  # Return the removed movie title
    else:
        print("Invalid index.")  # Inform the user of an invalid selection
        return None
    
def analyze_emotions(text):
    if not text.strip():  # Ensure the text is not empty
        return []
    results = emotion_classifier(text)  # Get emotion scores from the classifier
    emotion_counts = {}
    for classification in results[0]:
        emotion = classification['label'].lower()  # Get the emotion label
        score = classification['score']  # Get the confidence score
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + score  # Aggregate scores per emotion
    # Sort emotions by their aggregated scores in descending order
    sorted_emotions = sorted(emotion_counts.items(), key=lambda item: item[1], reverse=True)
    # Return the top 3 emotions or fewer if not available
    top_emotions = [emotion for emotion, score in sorted_emotions[:3]]
    return top_emotions

def categorize_year(year):
    try:
        year = int(year)  # Convert year to integer
        if year <= 1999:
            return "old"
        elif 2000 <= year <= 2009:
            return "middle"
        elif 2010 <= year <= 2019:
            return "new"
        elif 2020 <= year <= 2024:
            return "very new"
    except ValueError:
        return None  # Return None if year is not a valid integer
    

##Scraping functions are here. This functions were taken from pavan412kalyan user on Github, but renewed based on current structure of IMDB and to take only one most supported review of a movie
##https://github.com/pavan412kalyan/imdb-movie-scraper

def extract_helpful_votes(review_container):
    """
    Extracts the number of helpful votes from a review container.
    
    Parameters:
        review_container (BeautifulSoup object): The HTML container of a single review.
    
    Returns:
        int: The number of helpful votes. Returns 0 if not found or invalid.
    """
    helpful_span = review_container.find('span', {'class': 'ipc-voting__label__count--up'})
    if helpful_span:
        try:
            helpful_text = helpful_span.text.strip()
            if 'K' in helpful_text:
                # Convert "1.5K" to 1500
                return int(float(helpful_text.replace('K', '')) * 1000)
            return int(helpful_text)  # Convert the number string to integer
        except ValueError:
            return 0  # Return 0 if conversion fails
    return 0  # Return 0 if the helpful_span is not found

def scrape_most_supported_review(soup):
    """
    Scrapes the most supported review from the BeautifulSoup object of the reviews page.
    
    Parameters:
        soup (BeautifulSoup object): Parsed HTML of the IMDb reviews page.
    
    Returns:
        dict or None: A dictionary containing review details or None if no reviews are found.
    """
    # Find all review containers on the page
    review_containers = soup.find_all('div', {'class': 'ipc-list-card__content'})

    if not review_containers:
        return None  # Return None if no reviews are found

    most_supported_review = None
    max_helpful_votes = -1

    # Iterate through each review container to find the one with the most helpful votes
    for container in review_containers:
        helpful_votes = extract_helpful_votes(container)  # Get the number of helpful votes

        # Update the most_supported_review if this review has more votes
        if helpful_votes > max_helpful_votes:
            max_helpful_votes = helpful_votes
            most_supported_review = container

    if not most_supported_review:
        return None  # Return None if no supported review is found

    # Extract details from the most supported review
    review_data = {}

    # Extract the rating given in the review (if available)
    rating_span = most_supported_review.find('span', {'class': 'ipc-rating-star--rating'})
    review_data['rating'] = rating_span.text.strip() if rating_span else "No rating"

    # Extract the title of the review
    title = most_supported_review.find('h3', {'class': 'ipc-title__text'})
    review_data['title'] = title.text.strip() if title else "No title"

    # Extract the full text of the review
    review_text_div = most_supported_review.find('div', {'class': 'ipc-html-content-inner-div'})
    review_data['full_review'] = (
        review_text_div.text.strip() if review_text_div else "No review text"
    )

    # Include the number of helpful votes in the review data
    review_data['helpful_votes'] = max_helpful_votes

    return review_data  # Return the dictionary containing review details

def fetch_most_supported_review(movie_url):
    """
    Fetches and returns the most supported review from the specified IMDb URL.
    
    Parameters:
        movie_url (str): The URL of the IMDb reviews page for a specific movie.
    
    Returns:
        str or None: The full text of the most supported review or None if not found.
    """
    try:
        # Make a GET request to the IMDb reviews page with a user-agent header
        response = requests.get(movie_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    except requests.exceptions.RequestException:
        return None  # Return None if the request fails

    if response.status_code != 200:
        return None  # Return None if the HTTP status is not OK

    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

    # Scrape the most supported review using the previously defined function
    review_data = scrape_most_supported_review(soup)

    if review_data:
        return review_data['full_review']  # Return only the review text
    else:
        return None  # Return None if no review is found
    
# Function to determine sentiment ('like' or 'dislike') using TextBlob
def determine_sentiment(review):
    """
    Determines the sentiment of a review using TextBlob.
    
    Parameters:
        review (str): The text of the user's review.
    
    Returns:
        str: 'like' if sentiment polarity is >= 0.1, otherwise 'dislike'.
    """
    blob = TextBlob(review)
    polarity = blob.sentiment.polarity  # Get the sentiment polarity (-1 to 1)
    if polarity >= 0.1:
        return "like"  # Positive sentiment
    else:
        return "dislike"  # Negative or neutral sentiment
    
def recommend_based_on_preferences(preferences, full_titles, ratings):
    """
    Recommends up to three movies based on user preferences, matching genres and emotions.
    
    Parameters:
        preferences (dict): User preferences containing genres, emotions, and year category.
        full_titles (list): List of all movies with their details from 'full_title.basics.tsv'.
        ratings (list): List of movie ratings from 'title.ratings.tsv'.
    
    Returns:
        None
    """
    recommended = []  # List to store recommended movie titles
    watch_later = read_watch_later()  # Read current watch later list
    watched = read_watched()  # Read watched movies
    watched_titles = [movie['title'].lower() for movie in watched]  # Lowercase titles for comparison
    watch_later_titles = [title.lower() for title in watch_later]  # Lowercase titles for comparison

    # Create a dictionary for quick lookup of ratings by movie ID (tconst)
    ratings_dict = {rating['tconst']: rating for rating in ratings}

    # Convert preferred genres and emotions to lowercase for case-insensitive matching
    preferred_genres_lower = [g.lower() for g in preferences['Genres']]
    preferred_emotions_lower = [e.lower() for e in preferences['Emotions']]

    # Determine the required number of genre and emotion matches based on user preferences
    # If the user has two or more preferred genres/emotions, require at least two matches
    # Otherwise, require at least one match
    required_genre_matches = 2 if len(preferences['Genres']) >= 2 else 1
    required_emotion_matches = 2 if len(preferences['Emotions']) >= 2 else 1

    # Iterate through all movies to find suitable recommendations
    for movie in full_titles:
        if len(recommended) >= 3:
            break  # Limit to three recommendations

        # Extract genres of the current movie
        movie_genres = movie['genres'].split(',') if movie['genres'] else []
        # Count how many genres match the user's preferred genres
        genre_matches = sum(1 for genre in movie_genres if genre.strip().lower() in preferred_genres_lower)
        if genre_matches < required_genre_matches:
            continue  # Skip movies that don't meet the genre match requirement

        # Categorize the movie's release year
        movie_year_category = categorize_year(movie['startYear'])
        if not movie_year_category or (preferences['Year'] and movie_year_category != preferences['Year']):
            continue  # Skip if year category doesn't match user preference

        # Check if the movie has already been watched or is in the watch later list
        if movie['originalTitle'].lower() in watched_titles or movie['originalTitle'].lower() in watch_later_titles:
            continue  # Skip already watched or watch later movies

        # Retrieve the rating and number of votes for the movie
        rating = ratings_dict.get(movie['tconst'])
        if not rating:
            continue  # Skip if rating information is missing
        try:
            average_rating = float(rating['averageRating'])  # Convert rating to float
            num_votes = int(rating['numVotes'])  # Convert votes to integer
        except ValueError:
            continue  # Skip if rating or votes are invalid
        if average_rating <= 6.5 or num_votes <= 50000:
            continue  # Skip movies that don't meet the rating and vote criteria

        # Fetch the most supported review for the movie from IMDb
        movie_code = movie['tconst']
        movie_url = f"https://www.imdb.com/title/{movie_code}/reviews"  # Construct the reviews URL
        review_text = fetch_most_supported_review(movie_url)
        if not review_text:
            continue  # Skip if no review is found

        # Analyze emotions present in the fetched review
        emotions = analyze_emotions(review_text)
        # Count how many emotions match the user's preferred emotions
        emotion_matches = sum(1 for emotion in emotions if emotion.strip().lower() in preferred_emotions_lower)
        if emotion_matches < required_emotion_matches:
            continue  # Skip movies that don't meet the emotion match requirement

        # If all criteria are met, add the movie to the recommended list and watch later list
        recommended.append(movie['originalTitle'])
        append_watch_later(movie['originalTitle'])

        # Retrieve additional information for display
        year = movie['startYear']
        genres = movie['genres']
        rating_value = average_rating
        print(f"Recommended Movie: {movie['originalTitle']} ({year}) | Genres: {genres} | Rating: {rating_value}")
        
        time.sleep(1)  # Pause to prevent overwhelming IMDb with requests

    # Inform the user about the recommendation outcome
    if recommended:
        print("\nRecommended movies have been added to your watch later list.")
    else:
        print("\nNo recommendations found based on your current preferences.")

def renew_preferences(full_titles):
    """
    Allows the user to renew their preferences by adding new watched movies and updating genres, emotions, and year preferences.
    - All preferences (Genres, Emotions, Year) are based solely on the movies entered during the current renewal session.
    - The watched list is updated with the new movies, but previous entries do not influence the new preferences.
    
    Parameters:
        full_titles (list): List of all movies with their details from 'full_title.basics.tsv'.
    
    Returns:
        None
    """
    # Clear existing preferences to start fresh
    preferences = {
        'Genres': [],
        'Emotions': [],
        'Year': ''
    }
    write_preferences(preferences)  # Reset preferences.txt
    
    print("\nRenewing preferences...")
    
    # List to store newly entered movies during this renewal session
    new_movies = []
    
    # Prompt the user to enter favorite movies and their reviews
    print("Enter your favorite movies and reviews. Type 'stop' when you're done.")
    while True:
        title_input = input("Enter your favorite movie title (or type 'stop' to finish): ").strip()
        if title_input.lower() == 'stop':
            break  # Exit the loop if the user types 'stop'
        if not title_input:
            print("Title cannot be empty. Please try again.")
            continue  # Prompt again if the title is empty
        
        # Search for movies matching the entered title (case-insensitive)
        matching_movies = [movie for movie in full_titles if movie['originalTitle'].lower() == title_input.lower()]
        
        if not matching_movies:
            print(f"No movies found with the title '{title_input}'. Please try again.")
            continue  # Prompt again if no matches are found
        
        # Handle cases where multiple movies have the same title by different release years
        if len(matching_movies) > 1:
            print(f"Multiple movies found with the title '{title_input}':")
            for idx, movie in enumerate(matching_movies, start=1):
                print(f"{idx}. {movie['originalTitle']} ({movie['startYear']}) | Genres: {movie['genres']}")
            while True:
                try:
                    # Prompt the user to select the correct movie by number
                    selection = int(input("Enter the number of the movie you have watched: ").strip())
                    if 1 <= selection <= len(matching_movies):
                        selected_movie = matching_movies[selection - 1]
                        break  # Exit the loop if a valid selection is made
                    else:
                        print("Invalid selection. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            selected_movie = matching_movies[0]  # Only one match found
        
        # Prompt the user to enter a review for the selected movie
        review = input("Enter your review for the movie: ").strip()
        if not review:
            print("Review cannot be empty. Please try again.")
            continue  # Prompt again if the review is empty
        
        # Determine the sentiment of the review ('like' or 'dislike')
        sentiment = determine_sentiment(review)
        
        # Append the movie and its review to the watched list
        append_watched(selected_movie['originalTitle'], review, sentiment)
        print(f"Movie '{selected_movie['originalTitle']}' has been added to your watched list with a status of '{sentiment}'.")
        
        # Add the selected movie details and review to the new_movies list for preference calculation
        new_movies.append({
            'originalTitle': selected_movie['originalTitle'],
            'startYear': selected_movie['startYear'],
            'genres': selected_movie['genres'],
            'review': review  # Include the review in the new_movies entry
        })
    
    # If no new movies were entered, inform the user and exit
    if not new_movies:
        print("No new movies were entered. Preferences remain unchanged.")
        return
    
    # -------------------
    # Update Genres Based on New Movies Only
    # -------------------
    genres_count = {}
    for movie in new_movies:
        if movie['genres']:
            genres = movie['genres'].split(',')
            for genre in genres:
                genre = genre.strip()
                if genre:
                    genres_count[genre] = genres_count.get(genre, 0) + 1  # Count each genre
    
    # Sort genres by their count in descending order and select the top 3
    sorted_genres = sorted(genres_count.items(), key=lambda item: item[1], reverse=True)
    top_genres = [genre for genre, count in sorted_genres[:3]]
    preferences['Genres'] = top_genres  # Update genres preference
    
    # -------------------
    # Update Year Preference Based on New Movies Only
    # -------------------
    # Extract and collect release years from the newly entered movies
    new_years = []
    for movie in new_movies:
        start_year = movie['startYear']
        if start_year:
            try:
                year = int(start_year)
                new_years.append(year)
            except ValueError:
                print(f"Invalid year format for movie '{movie['originalTitle']}': {start_year}")
                continue  # Skip if year is not a valid integer
    
    # Debug: Print the collected new years
    print(f"Collected Years from New Movies: {new_years}")
    
    # Determine the average year from the new_movies list
    if new_years:
        average_year = sum(new_years) / len(new_years)
        print(f"Average Year Calculated from New Movies: {average_year}")  # Debug statement
        
        # Categorize the average year
        if average_year <= 1999:
            year_category = "old"
        elif 2000 <= average_year <= 2009:
            year_category = "middle"
        elif 2010 <= average_year <= 2019:
            year_category = "new"
        elif 2020 <= average_year <= 2024:
            year_category = "very new"
        else:
            year_category = "unknown"  # For years outside the defined ranges
        preferences['Year'] = year_category
        print(f"Year Category Assigned based on New Movies: {year_category}")  # Debug statement
    else:
        preferences['Year'] = "new"  # Default if no valid years are found
        print("No valid years found in new movies. Defaulting Year Preference to 'new'.")  # Debug statement
    
    # -------------------
    # Update Emotions Based on New Movies Only
    # -------------------
    emotions_count = {}
    for movie in new_movies:
        review = movie['review']
        emotions = analyze_emotions(review)  # Get emotions from the review
        for emotion in emotions:
            emotion = emotion.lower()
            emotions_count[emotion] = emotions_count.get(emotion, 0) + 1  # Count each emotion
    
    # Sort emotions by their count in descending order and select the top 3
    sorted_emotions = sorted(emotions_count.items(), key=lambda item: item[1], reverse=True)
    top_emotions = [emotion for emotion, count in sorted_emotions[:3]]
    preferences['Emotions'] = top_emotions  # Update emotions preference
    
    # -------------------
    # Write Updated Preferences
    # -------------------
    write_preferences(preferences)
    print("\nPreferences have been updated successfully!")
    print(f"Genres: {', '.join(preferences['Genres'])}")
    print(f"Emotions: {', '.join(preferences['Emotions'])}")
    print(f"Year: {preferences['Year']}")

def search_by_title(full_titles, ratings):
    """
    Allows the user to search for a movie by its title and displays detailed information.
    
    Parameters:
        full_titles (list): List of all movies with their details from 'full_title.basics.tsv'.
        ratings (list): List of movie ratings from 'title.ratings.tsv'.
    
    Returns:
        None
    """
    title_input = input("Enter the movie title you want to search for: ").strip().lower()
    if not title_input:
        print("Movie title cannot be empty.")
        return  # Exit if the title is empty

    # Find all movies matching the input title (case-insensitive)
    matching_movies = [movie for movie in full_titles if movie['originalTitle'].lower() == title_input]

    if not matching_movies:
        print(f"No movies found with the title '{title_input}'.")
        return  # Inform the user if no matches are found

    # If multiple matches are found, list them with their release years and genres
    if len(matching_movies) > 1:
        print(f"Multiple movies found with the title '{title_input}':")
        for idx, movie in enumerate(matching_movies, start=1):
            print(f"{idx}. {movie['originalTitle']} ({movie['startYear']}) | Genres: {movie['genres']}")
        while True:
            try:
                # Prompt the user to select the correct movie by number
                selection = int(input("Enter the number of the movie you want details for: ").strip())
                if 1 <= selection <= len(matching_movies):
                    selected_movie = matching_movies[selection - 1]
                    break  # Exit the loop if a valid selection is made
                else:
                    print("Invalid selection. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        selected_movie = matching_movies[0]  # Only one match found

    # Retrieve the rating and number of votes for the selected movie
    rating = next((r for r in ratings if r['tconst'] == selected_movie['tconst']), None)
    if not rating:
        print(f"No rating data found for '{selected_movie['originalTitle']}'.")
        return  # Inform the user if rating data is missing
    try:
        average_rating = float(rating['averageRating'])  # Convert rating to float
        num_votes = int(rating['numVotes'])  # Convert votes to integer
    except ValueError:
        print(f"Invalid rating or vote data for '{selected_movie['originalTitle']}'.")
        return  # Inform the user if conversion fails

    # Fetch the most supported review for the selected movie
    movie_code = selected_movie['tconst']
    movie_url = f"https://www.imdb.com/title/{movie_code}/reviews"  # Construct the reviews URL
    review_text = fetch_most_supported_review(movie_url)
    if not review_text:
        print(f"No reviews found for '{selected_movie['originalTitle']}'.")
        return  # Inform the user if no review is found

    # Display the movie information and the fetched review
    print(f"\n--- Movie Information ---")
    print(f"Title: {selected_movie['originalTitle']}")
    print(f"Year: {selected_movie['startYear']}")
    print(f"Genres: {selected_movie['genres']}")
    print(f"Rating: {average_rating} ({num_votes} votes)")
    print(f"Review:\n{review_text}\n")



# Function to handle the "Search by Title" option in the main menu
def search_by_title_option():
    """
    Handles the "Search by Title" option by reading necessary data files and invoking the search function.
    
    Returns:
        None
    """
    full_titles = read_tsv(FULL_TITLE_FILE)  # Read all movie details
    ratings = read_tsv(TITLE_RATINGS_FILE)  # Read all movie ratings
    search_by_title(full_titles, ratings)  # Invoke the search function

# Function to initiate the recommendation process based on preferences
def recommend_movie():
    """
    Initiates the movie recommendation process by reading data files and user preferences.
    
    Returns:
        None
    """
    full_titles = read_tsv(FULL_TITLE_FILE)  # Read all movie details
    ratings = read_tsv(TITLE_RATINGS_FILE)  # Read all movie ratings
    preferences = read_preferences()  # Read user preferences
    # Check if preferences are set; if not, prompt the user to renew preferences first
    if not preferences['Genres'] and not preferences['Emotions'] and not preferences['Year']:
        print("Preferences are not set. Please renew preferences first.")
        return
    recommend_based_on_preferences(preferences, full_titles, ratings)  # Generate recommendations

# Function to handle the "Renew Preferences" option in the recommendation submenu
def renew_preferences_menu():
    """
    Handles the "Renew Preferences" option by reading data files and invoking the renew preferences function.
    
    Returns:
        None
    """
    full_titles = read_tsv(FULL_TITLE_FILE)  # Read all movie details
    renew_preferences(full_titles)  # Invoke the renew preferences function

def view_watched_list():
    """
    Displays the watched movies list and allows the user to add new movies with reviews.
    
    Returns:
        None
    """
    watched = read_watched()  # Read the watched list
    if not watched:
        print("\nYour watched list is empty.")
    else:
        print("\nWatched Movies:")
        for movie in watched:
            # Display each watched movie with its number, title, review, and status
            print(f"{movie['number']}. {movie['title']}: {movie['review']} ({movie['status']})")
    # Prompt the user to add a new movie to the watched list
    choice = input("\nDo you want to add a movie to your watched list? (yes/no): ").strip().lower()
    if choice == 'yes':
        while True:
            title = input("Enter the movie title (or type 'stop' to finish adding): ").strip()
            if title.lower() == 'stop':
                break  # Exit the loop if the user types 'stop'
            if not title:
                print("Title cannot be empty. Please try again.")
                continue  # Prompt again if the title is empty
            review = input("Enter your review: ").strip()
            if not review:
                print("Review cannot be empty. Please try again.")
                continue  # Prompt again if the review is empty
            sentiment = determine_sentiment(review)  # Determine the sentiment of the review
            append_watched(title, review, sentiment)  # Add the movie to the watched list
            print(f"Movie '{title}' has been added to your watched list with a status of '{sentiment}'.")

def view_watch_later_list():
    """
    Displays the watch later list and allows the user to add or remove movies.
    
    Returns:
        None
    """
    watch_later = read_watch_later()  # Read the watch later list
    if not watch_later:
        print("\nYour watch later list is empty.")
    else:
        print("\nWatch Later Movies:")
        for idx, title in enumerate(watch_later, start=1):
            # Display each watch later movie with its number and title
            print(f"{idx}. {title}")
    # Present options to the user for managing the watch later list
    while True:
        print("\nOptions:")
        print("1. Add a new movie")
        print("2. Remove a movie")
        print("3. Go back to menu")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            title = input("Enter the movie title to add: ").strip()
            if not title:
                print("Title cannot be empty. Please try again.")
                continue  # Prompt again if the title is empty
            append_watch_later(title)  # Add the movie to the watch later list
            print(f"Movie '{title}' has been added to your watch later list.")
        elif choice == '2':
            watch_later = read_watch_later()  # Refresh the watch later list
            if not watch_later:
                print("Watch later list is empty.")
                continue  # Inform the user if the list is empty
            try:
                index = int(input("Enter the number of the movie to remove: ").strip()) - 1
                if 0 <= index < len(watch_later):
                    removed = remove_watch_later(index)  # Remove the selected movie
                    if removed:
                        print(f"Movie '{removed}' has been removed from your watch later list.")
                        # Prompt the user to either delete the movie or move it to the watched list
                        while True:
                            action = input("Do you want to delete it or move to watched list? (delete/move): ").strip().lower()
                            if action == 'delete':
                                print(f"Movie '{removed}' has been deleted.")
                                break  # Exit the loop after deletion
                            elif action == 'move':
                                review = input("Enter your review for the movie: ").strip()
                                if not review:
                                    print("Review cannot be empty. Please try again.")
                                    continue  # Prompt again if the review is empty
                                sentiment = determine_sentiment(review)  # Determine the sentiment of the review
                                append_watched(removed, review, sentiment)  # Move the movie to the watched list
                                print(f"Movie '{removed}' has been moved to your watched list with a status of '{sentiment}'.")
                                break  # Exit the loop after moving
                            else:
                                print("Invalid choice. Please enter 'delete' or 'move'.")
                else:
                    print("Invalid number.")  # Inform the user of an invalid selection
            except ValueError:
                print("Please enter a valid number.")  # Handle non-integer inputs
        elif choice == '3':
            break  # Exit the loop and return to the main menu
        else:
            print("Invalid choice. Please select again.")  # Handle invalid menu options


def handle_recommendation():
    """
    Handles the recommendation submenu, allowing the user to choose between recommending movies,
    renewing preferences, or going back to the main menu.
    
    Returns:
        None
    """
    while True:
        display_recommendation_menu()  # Show the recommendation submenu
        choice = input("Choose an option: ").strip()
        if choice == '1':
            recommend_movie()  # Generate recommendations based on preferences
        elif choice == '2':
            renew_preferences_menu()  # Allow the user to renew preferences
        elif choice == '3':
            break  # Exit the recommendation submenu and return to the main menu
        else:
            print("Invalid choice. Please select again.")  # Handle invalid submenu options


def main():
    """
    The main loop of the Movie Match program. Displays the main menu and handles user selections.
    
    Returns:
        None
    """
    while True:
        display_main_menu()  # Show the main menu
        choice = input("Choose an option: ").strip()
        if choice == '1':
            handle_recommendation()  # Handle movie recommendations
        elif choice == '2':
            view_watched_list()  # Display and manage the watched list
        elif choice == '3':
            view_watch_later_list()  # Display and manage the watch later list
        elif choice == '4':
            search_by_title_option()  # Allow the user to search for a movie by title
        elif choice == '5' or choice.lower() == 'quit':
            print("Exiting Movie Match. Goodbye!")
            sys.exit()  # Exit the program
        else:
            print("Invalid choice. Please select again.")  # Handle invalid main menu options

if __name__ == "__main__":
    main()