from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import difflib
import os

# Load pickle files with error handling
try:
    base_path = r"C:\Users\gauri kad\OneDrive\Desktop\BRS"
    popular_df = pd.read_pickle(os.path.join(base_path, "popular.pkl")) 
    pt = pd.read_pickle(os.path.join(base_path, "pt.pkl"))  
    books = pd.read_pickle(os.path.join(base_path, "books.pkl"))  
    similarity_scores = pd.read_pickle(os.path.join(base_path, "similarity_scores.pkl"))
    # book_titles = pd.read_pickle(os.path.join(base_path, "book_titles.pkl"))  
except Exception as e:
    print(f"Error loading model files: {e}")
    exit(1)

book_titles = list(pt.index)




# Find books in book_titles but missing in pt.index
# missing_books = set(book_titles) - set(pt.index)
# print("Missing books:", missing_books)

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           book_titles=book_titles
                           )

# Recommendation page UI
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html', book_titles=book_titles)

# Recommendation function
@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input').strip()

    # Find the closest match
    closest_match = difflib.get_close_matches(user_input, pt.index, n=1)

    if not closest_match:
        return render_template('recommend.html', book_titles=book_titles, error=f"No exact match found for '{user_input}'.", selected_book=user_input)

    book_name = closest_match[0]

    # Check if book exists in pt index
    index_array = np.where(pt.index == book_name)[0]
    if len(index_array) == 0:
        return render_template('recommend.html', book_titles=book_titles, error=f"'{book_name}' not found in recommendations.", selected_book=user_input)

    index = index_array[0]

    # Get similar books
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

        if not temp_df.empty:
            item = [
                temp_df.iloc[0]['Book-Title'],
                temp_df.iloc[0]['Book-Author'],
                temp_df.iloc[0]['Image-URL-M'],
            ]
            data.append(item)

    return render_template('recommend.html', data=data, book_titles=book_titles, selected_book=user_input)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
