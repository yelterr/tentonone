from flask import Flask, render_template, redirect, url_for, send_from_directory, request, jsonify
import os
import pathlib
import random
from oursql import credentials, create_db_connection, add_row, get_current_rating, get_all_average_ratings, get_ranking, get_count
from send_email import send_email

# TODO - Delete this when you implement the name retrieval from the name table
import numpy as np

# TODO - MOVE IMAGES OUTSIDE OF STATIC (GENERAL TASK, NEEDS SOME FUNCTION CHANGES PROBABLY)

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
@app.route('/rate')
def start_game():
    random_image = get_random_image(gender_choice)
    name = get_name(random_image)

    global last_image
    last_image = random_image

    return render_template("game.html", random_image=random_image, name=name)

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

# Provides the Javascript function with a random image
@app.route("/get_image")
def get_image():
    image_path = get_random_image(gender_choice)
    global last_image
    last_image = image_path

    name = get_name(image_path)

    result = {"impath" : image_path, "name" : name}

    return jsonify(result=result)

# Recieves the rating, amt_raters, ranking from the submit button
@app.route("/send_rating", methods=["POST"])
def send_rating():
    data = request.get_json()

    link = data["image_path"]
    filename = extract_filename(link)

    rating = float(data["slider_value"])
    add_row(db_connection, filename, rating)
    rating_now = get_current_rating(db_connection, filename)

    if rating_now == -1:
        rating_now = "[Error, please report this to us]"

    amt_raters = get_count(db_connection, filename)
    ranking = get_ranking(db_connection, filename)

    result = {"rating" : rating_now, "amt_raters" : amt_raters, "ranking" : ranking}

    return jsonify(result=result)

# Updates the gender_choice variable
@app.route("/update_gender_choice", methods=["POST"])
def update_gender_choice():
    data = request.get_json()
    global gender_choice
    gender_choice = data["gender_choice"]
    return "It worked"

@app.route("/retrieve_ratings", methods=["POST"])
def retrieve_the_ratings():
    data = request.get_json()
    filter = data["filterChoice"]
    
    rankings = get_filtered_lines(filter)

    return jsonify(result=rankings)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Instead of php, I'm using this to process the messages from the contact us page.
@app.route('/submit_form', methods=['POST'])
def submit_form():
    form_data = request.form
    send_email(form_data)

    return render_template("contact.html", form_submit=True)

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
    while chosen_image == last_image:
        print(f"Filename: {chosen_image}")
        print(f"Last Image: {last_image}")
        chosen_image = get_random_image(gender_choice)

    return chosen_image

# Cleans floats so that there are no unnecessary digits on the leaderboard
def clean_num(num):
    to_clean = list(str(num))[::-1]

    # Clean the repeating numbers
    if len(to_clean) >= 7:
            if set(to_clean[1:4]) == set(to_clean[1]):
                if int(to_clean[0]) == int(to_clean[1]) + 1:
                    to_clean.pop(1)
                    to_clean.pop(2)
                    return float("".join(to_clean[::-1]))

    for i, digit in enumerate(to_clean):
        if digit == "0":
            to_clean[i] = ""
        else:
            break
    
    return float("".join(to_clean[::-1]))

# TODO - in name table, add gender and change this to querying that table instead of checking the lists of folders.
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
        final_ratings = ratings
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

    # Adding rank to lines
    for i, rating in enumerate(final_ratings):
        line = list(rating)
        line[-1] = clean_num(line[-1])
        if filter == "l2h":
            line.append(len(final_ratings)-i)
            # TODO - Implement get_name() function so that this works
            line.append(get_name(rating[0]))
            final_ratings[i] = tuple(line)
        else:
            line.append(i+1)
            # TODO - Implement get_name() function so that this works
            line.append(get_name(rating[0]))
            final_ratings[i] = tuple(line)

    return final_ratings

def extract_filename(filepath):
    index = filepath.index("static")
    return filepath[index:]

# TODO - Implement the actual gathering of names from the name table
def get_name(impath):
    name = np.random.choice(["Joao Pereira", "Johnny Depp", "Margaret Thatcher", "Charles Bukowski"])
    return name

if __name__ == '__main__':
    app.run(debug=True)