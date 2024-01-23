from flask import Flask, render_template, redirect, url_for, send_from_directory, request, jsonify
import os
import pathlib
import random
from oursql import credentials, create_db_connection, add_row, get_current_rating, get_all_average_ratings

# TODO - Delete this when you implement the name retrieval from the name table
import numpy as np

app = Flask(__name__)
gender_choice = "both"
last_image = None

db = "hotornot"
db_connection = create_db_connection(credentials.host, credentials.username, credentials.passwd, db)

# Loads the main menu
@app.route('/')
def index():
    return render_template('index.html')

# Begins the game by loading the game template and providing the first image
@app.route('/game')
def start_game():
    random_image = get_random_image(gender_choice)
    
    filename = extract_filename(random_image)
    name = get_name(filename)

    global last_image
    last_image = filename

    return render_template("game.html", random_image=random_image, name=name)

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

# Provides the Javascript function with a random image
@app.route("/get_image")
def get_image():
    image_path = get_random_image(gender_choice)
    global last_image
    last_image = extract_filename(image_path)

    name = get_name(last_image)

    result = {"impath" : image_path, "name" : name}

    return jsonify(result=result)

# Recieves the rating from the submit button
@app.route("/send_rating", methods=["POST"])
def send_rating():
    data = request.get_json()

    link = data["image_path"]
    print(link)
    filename = link[::-1][:link[::-1].index("/")][::-1]

    rating = float(data["slider_value"])
    add_row(db_connection, filename, rating)
    rating_now = get_current_rating(db_connection, filename)

    if rating_now == -1:
        rating_now = "[Error, please report this to us]"

    return jsonify(result=str(rating_now))

# Updates the gender_choice variable
@app.route("/update_gender_choice", methods=["POST"])
def update_gender_choice():
    data = request.get_json()
    global gender_choice
    gender_choice = data["gender_choice"]
    return "It worked"

# Retrieves a random image path from the images directory
def get_random_image(gender_choice):
    if gender_choice == "men":
        all_men_images = list(pathlib.Path("static/images/").glob("men/*.jpg"))
        random_impath = random.choice(all_men_images)
        chosen_image = str(random_impath)
    elif gender_choice == "women":
        all_women_images = list(pathlib.Path("static/images/").glob("women/*.jpg"))
        random_impath = random.choice(all_women_images)
        chosen_image = str(random_impath)
    else: # When gender_choice == "both" or any other circumstance
        all_images = list(pathlib.Path("static/images/").glob("*/*.jpg"))
        random_impath = random.choice(all_images)
        chosen_image = str(random_impath)

    # Making sure that the new image is not the same as the last image (rare, but just in case)
    just_filename = extract_filename(chosen_image)
    while just_filename == last_image:
        print(f"Filename: {just_filename}")
        print(f"Last Image: {last_image}")
        chosen_image = get_random_image(gender_choice)
        just_filename = extract_filename(chosen_image)

    return chosen_image

def get_filtered_lines(filter="h2l"):
    ratings = get_all_average_ratings(db_connection)

    # Sorting by highest to lowest or reverse
    if filter == "h2l":
        ratings = sorted(ratings, key=(lambda x : x[2]))[::-1]
    elif filter == "l2h":
        ratings = sorted(ratings, key=(lambda x : x[2]))

    # Filtering for gender
    final_ratings = []
    if gender_choice == "both":
        return ratings
    else:
        all_men_images = list(pathlib.Path("static/images/").glob("men/*.jpg"))
        all_women_images = list(pathlib.Path("static/images/").glob("women/*.jpg"))

        if gender_choice == "men":
            for rating in ratings:
                if any(rating[0] in str(s) for s in all_men_images):
                    final_ratings.append(rating)

        elif gender_choice == "women":
            for rating in ratings:
                if any(rating[0] in str(s) for s in all_women_images):
                    final_ratings.append(rating)


    return final_ratings

def extract_filename(filepath):
    return filepath[::-1][:filepath[::-1].index("/")][::-1]

# TODO - Implement the actual gathering of names from the name table
def get_name(filename):
    name = np.random.choice(["Joao Pereira", "Johnny Depp", "Margaret Thatcher", "Charles Bukowski"])
    return name

@app.route("/retrieve_ratings", methods=["POST"])
def retrieve_the_ratings():
    data = request.get_json()
    filter = data["filterChoice"]
    

    ratings = get_filtered_lines(filter)
    return jsonify(result=ratings)

if __name__ == '__main__':
    app.run(debug=True)