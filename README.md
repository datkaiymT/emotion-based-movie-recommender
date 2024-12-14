# Movie Match

**Movie Match** is a Python-based command-line application developed to provide personalized movie recommendations tailored to individual user preferences. By analyzing previously watched movies and accompanying reviews, Movie Match identifies key genres and emotional tones that align with the user's tastes. Leveraging data from IMDb, natural language processing (NLP), and sentiment analysis, the application offers curated movie suggestions that resonate with the user's unique preferences.

---

## Table of Contents

- [Features](#features)
- [Technologies and Libraries Used](#technologies-and-libraries-used)
- [Installation and Setup](#installation-and-setup)
- [Data Files](#data-files)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Example Interaction](#example-interaction)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Personalized Recommendations**: Suggests up to three movies based on user-defined genres, emotions, and preferred release years.
- **Emotion Analysis**: Utilizes advanced NLP models to discern the emotional undertones of user reviews.
- **Dynamic Matching Criteria**: Adjusts recommendation thresholds based on the number of user-specified genres and emotions.
- **Watch Lists Management**:
  - **Watched List**: Logs movies the user has viewed, along with their reviews and sentiment classifications (`like` or `dislike`).
  - **Watch Later List**: Allows users to save recommended movies for future viewing.
- **Search Functionality**: Enables users to search for specific movies by title and retrieve detailed information.
- **Handling Duplicate Titles**: Identifies and manages movies with identical titles released in different years, ensuring accurate user selections.
- **Polite Scraping Practices**: Incorporates delays between web requests to respect IMDb's server load and avoid IP blocking.

---
## 🎥 Tutorial

[![Watch the Movie Match Tutorial](https://img.youtube.com/vi/4bAA-9oEhqE/0.jpg)](https://www.youtube.com/watch?v=4bAA-9oEhqE)

*Click the thumbnail above to watch the tutorial video.*
---

## Technologies and Libraries Used

- **Python 3.7+**: The primary programming language used for development.
- **Transformers (HuggingFace)**: For emotion analysis using pre-trained NLP models.
- **Torch**: Backend library required by Transformers for model computations.
- **TextBlob**: Simplifies sentiment analysis of user reviews.
- **Requests**: Facilitates HTTP requests to fetch movie reviews from IMDb.
- **BeautifulSoup4**: Parses and scrapes HTML content from IMDb review pages.
- **NLTK (Natural Language Toolkit)**: Provides essential NLP tools required by TextBlob.

---

## Installation and Setup

Follow these steps to set up and run Movie Match on your local machine.

### 1. Upgrade `pip`

Ensure you have the latest version of `pip` to avoid installation issues.

```bash
pip install --upgrade pip
```

### 3. Install Required Python Libraries

Run the following command to install all necessary dependencies:

```bash
pip install transformers torch textblob requests beautifulsoup4 nltk
```


### 4. Download Necessary NLTK Data

**TextBlob** relies on NLTK data, specifically the `punkt` tokenizer. Download it by running the following Python commands:

**Interactive Python Shell:**

1. **Open Python Shell:**

   ```bash
   python
   ```

2. **Run the Following Commands:**

   ```python
   import nltk
   nltk.download('punkt')
   exit()
   ```

---

## Data Files

The application relies on two main data files sourced from IMDb:

1. **`full_title.basics.tsv`**
   - **Description**: Contains comprehensive details about each movie, including its unique identifier (`tconst`), original title, release year (`startYear`), and genres.
   - **Fields**:
     - `tconst`: Unique IMDb identifier for the movie (e.g., tt0111161).
     - `originalTitle`: The official title of the movie.
     - `startYear`: The year the movie was released.
     - `genres`: Comma-separated list of genres associated with the movie.

2. **`title.ratings.tsv`**
   - **Description**: Provides rating information for each movie, including the average rating and the number of votes it has received.
   - **Fields**:
     - `tconst`: Unique IMDb identifier for the movie.
     - `averageRating`: The movie's average rating on IMDb.
     - `numVotes`: The total number of votes the movie has received.

---

## How It Works

Movie Match operates through several interconnected components that work together to provide accurate and personalized movie recommendations. Here's a breakdown of its core functionalities:

### 1. **User Preferences Input**

- **Watched List**: Users input movies they've watched along with their reviews.
- **Preference Extraction**: The system analyzes these inputs to determine the user's preferred genres, emotional tones, and preferred release year categories.

### 2. **Emotion and Sentiment Analysis**

- **Emotion Analysis**: Utilizes the `nateraw/bert-base-uncased-emotion` model from HuggingFace's Transformers library to identify emotions present in user reviews.
- **Sentiment Analysis**: Employs TextBlob to classify user reviews as positive (`like`) or negative (`dislike`) based on the polarity of the text.

### 3. **Recommendation Generation**

- **Filtering Criteria**:
  - **Genres Matching**: Recommends movies that match a specified number of preferred genres (dynamic based on user input).
  - **Emotions Matching**: Ensures that the emotional tone of movie reviews aligns with user preferences.
  - **Rating and Popularity**: Considers only movies with an average rating above 6.5 and more than 50,000 votes to ensure quality recommendations.
- **Handling Duplicate Titles**: When users input movie titles that have multiple entries with different release years, the system prompts users to select the correct one, ensuring accurate data processing.

### 4. **Watch Lists Management**

- **Watched List**: Logs movies the user has watched, along with their reviews and sentiment classifications.
- **Watch Later List**: Stores recommended movies for future viewing, allowing users to manage their viewing queue effectively.

### 5. **Web Scraping for Reviews**

- **IMDb Integration**: Fetches the most supported reviews for movies directly from IMDb to analyze the emotional content.
- **Polite Scraping**: Incorporates delays between requests to avoid overwhelming IMDb's servers and to adhere to ethical scraping practices.

---

## Usage

Upon running the program, users are greeted with a menu-driven interface that guides them through various functionalities.

### **Main Menu Options**

1. **Recommend a Movie**
2. **View a Watched List**
3. **View a Watch Later List**
4. **Search by Title**
5. **Quit**

### **1. Recommend a Movie**

#### **Submenu Options**

1. **Recommend based on preferences**
2. **Renew preferences**
3. **Go back to menu**

- **Recommend based on preferences**: Generates movie recommendations based on your saved preferences.
- **Renew preferences**: Allows you to update your favorite movies and reviews, which in turn updates your preferences.
- **Go back to menu**: Returns to the main menu.

#### **Renew Preferences**

When renewing preferences:

1. **Enter Favorite Movies and Reviews**:
   - Input your favorite movie titles.
   - If multiple movies share the same title, you'll be prompted to select the correct one based on the release year.
   - Provide a personal review for each movie.

2. **Preference Extraction**:
   - **Genres**: Analyzes the genres of your watched movies and identifies the top three.
   - **Emotions**: Uses NLP to determine the most common emotions in your reviews.
   - **Year Category**: Categorizes your favorite movies based on their release years (old, middle, new, very new).

### **2. View a Watched List**

- Displays a list of movies you've watched along with your reviews and sentiment statuses (`like` or `dislike`).
- **Options**:
  - **Add a Movie**: You can add more movies to your watched list by providing the title and review.

### **3. View a Watch Later List**

- Shows movies you've saved to watch in the future.
- **Options**:
  - **Add a New Movie**: Add more movies to your watch later list.
  - **Remove a Movie**: Remove movies from the list. Upon removal, you can choose to either delete the movie or move it to your watched list with a review.

### **4. Search by Title**

- Allows you to search for specific movies by their title.
- If multiple movies share the same title, you'll be prompted to select the correct one based on the release year.
- Displays detailed information about the selected movie, including a sample review.

### **5. Quit**

- Exits the Movie Match application.

---

## Example Interaction

Below is a sample interaction showcasing the key functionalities of Movie Match.

### **1. Setting Preferences**

```
Welcome to Movie Match
1. Recommend a movie
2. View a watched list
3. View a watch later list
4. Search by title
5. Quit
Choose an option: 1

Recommend a Movie
1. Recommend based on preferences
2. Renew preferences
3. Go back to menu
Choose an option: 2

Renewing preferences...
Enter your favorite movies and reviews. Type 'stop' when you're done.
Enter your favorite movie title (or type 'stop' to finish): Batman
Multiple movies found with the title 'batman':
1. Batman (1989) | Genres: Action,Crime,Drama
2. Batman (2022) | Genres: Action,Adventure
Enter the number of the movie you have watched: 1
Enter your review for the movie: A classic portrayal of the dark knight with deep character development.
Movie 'Batman' has been added to your watched list with a status of 'like'.

Enter your favorite movie title (or type 'stop' to finish): Batman
Multiple movies found with the title 'batman':
1. Batman (1989) | Genres: Action,Crime,Drama
2. Batman (2022) | Genres: Action,Adventure
Enter the number of the movie you have watched: 2
Enter your review for the movie: A fresh and modern take on the iconic superhero.
Movie 'Batman' has been added to your watched list with a status of 'like'.

Enter your favorite movie title (or type 'stop' to finish): stop

Preferences have been updated successfully!
Genres: Action, Crime, Adventure
Emotions: positive, excitement
Year: old
```

### **2. Generating Recommendations**

```
Welcome to Movie Match
1. Recommend a movie
2. View a watched list
3. View a watch later list
4. Search by title
5. Quit
Choose an option: 1

Recommend a Movie
1. Recommend based on preferences
2. Renew preferences
3. Go back to menu
Choose an option: 1
Recommended Movie: The Godfather (1972) | Genres: Crime,Drama | Rating: 9.2
Recommended Movie: The Dark Knight (2008) | Genres: Action,Crime,Drama | Rating: 9.0
Recommended Movie: The Lord of the Rings: The Fellowship of the Ring (2001) | Genres: Action,Adventure,Drama | Rating: 8.8

Recommended movies have been added to your watch later list.
```

### **3. Searching for a Movie by Title**

```
Welcome to Movie Match
1. Recommend a movie
2. View a watched list
3. View a watch later list
4. Search by title
5. Quit
Choose an option: 4
Enter the movie title you want to search for: Batman

Multiple movies found with the title 'batman':
1. Batman (1989) | Genres: Action,Crime,Drama
2. Batman (2022) | Genres: Action,Adventure
Enter the number of the movie you want details for: 2

--- Movie Information ---
Title: Batman
Year: 2022
Genres: Action,Adventure
Rating: 6.8 (60000 votes)
Review:
A fresh and modern take on the iconic superhero.
```

---

## Troubleshooting

### **1. Module Not Found Errors**

**Issue**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:

- Ensure all dependencies are installed.
- Activate your virtual environment if you're using one.
- Re-run the installation command:

  ```bash
  pip install transformers torch textblob requests beautifulsoup4 nltk
  ```

### **2. NLTK Data Not Downloaded**

**Issue**: Errors related to missing NLTK data when running TextBlob.

**Solution**:

- Ensure you've downloaded the `punkt` tokenizer.

  ```python
  import nltk
  nltk.download('punkt')
  ```

### **3. IMDb Scraping Issues**

**Issue**: Reviews not being found or errors during scraping.

**Solution**:

- **Check IMDb's Page Structure**: IMDb may update its website, breaking the scraping logic.
  - Inspect the IMDb review page using browser developer tools.
  - Update the BeautifulSoup selectors in the `scrape_most_supported_review` function accordingly.
- **JavaScript-Rendered Content**: If reviews are loaded dynamically, consider using Selenium to render JavaScript.
  - **Note**: This adds complexity and requires additional setup.

### **4. Network Issues**

**Issue**: Unable to fetch reviews due to network instability or IMDb blocking requests.

**Solution**:

- **Stable Internet Connection**: Ensure your device is connected to the internet.
- **Implement Rate Limiting**: Increase `time.sleep()` durations between requests to prevent overwhelming IMDb's servers.
- **Respect IMDb's Terms**: Avoid excessive scraping to prevent IP blocking.

---

## Acknowledgments

- **IMDb**: For providing comprehensive movie data.
- **HuggingFace Transformers**: For their powerful NLP models.
- **TextBlob**: For simplifying sentiment analysis.
- **OpenAI**: For inspiring advancements in AI and machine learning.
- **Professors and Peers**: For their guidance and support during the development of this project.

---

**Enjoy personalized movie recommendations with Movie Match!**
