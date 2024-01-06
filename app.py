from flask import Flask, render_template, redirect, url_for, send_from_directory, request, jsonify
import os
import pathlib
import random

app = Flask(__name__)
gender_choice = "both"


# Loads the main menu
@app.route('/')
def index():
    return render_template('index.html')

# Begins the game by loading the game template and providing the first image
@app.route('/game')
def start_game():
    random_image = get_random_image(gender_choice)
    return render_template("game.html", random_image=random_image)

@app.route("/leaderboard")
def leaderboard():
    text_doc = "temp_ratings.txt"
    with open(text_doc, "r") as text:
        lines = text.readlines()

    lines = [line_extract(line) for line in lines]

    return render_template("leaderboard.html", lines=lines)

# Provides the Javascript function with a random image
@app.route("/get_image")
def get_image():
    image_path = get_random_image(gender_choice)
    return jsonify(result=image_path)

# Recieves the rating from the submit button
@app.route("/send_rating", methods=["POST"])
def send_rating():
    data = request.get_json()

    link = data["image_path"]
    filename = link[::-1][:link[::-1].index("/")][::-1]

    rating = float(data["slider_value"])
    rating_before = get_current_rating(filename)

    write_line(filename, rating)

    return jsonify(result=str(rating_before))

# Updates the gender_choice variable
@app.route("/update_gender_choice", methods=["POST"])
def update_gender_choice():
    data = request.get_json()
    global gender_choice
    gender_choice = data["gender_choice"]
    return "It worked"

# Retrieves a random image path from the images directory
def get_random_image(gender_choice):
    if gender_choice == "both":
        all_images = list(pathlib.Path("static/images/").glob("*/*.jpg"))
        random_impath = random.choice(all_images)
        return str(random_impath)
    elif gender_choice == "men":
        all_men_images = list(pathlib.Path("static/images/").glob("men/*.jpg"))
        random_impath = random.choice(all_men_images)
        return str(random_impath)
    elif gender_choice == "women":
        all_women_images = list(pathlib.Path("static/images/").glob("women/*.jpg"))
        random_impath = random.choice(all_women_images)
        return str(random_impath)
    else:
        print("WTF How did you choose that gender lmao???")

# Writes a line to temp_ratings.txt or updates an existing line
def write_line(filename, rating):
    line_written = False
    text_doc = "temp_ratings.txt"

    with open(text_doc, "r+") as text:
        lines = text.readlines()
        for i, line in enumerate(lines):
            if filename in line:
                line_written = True
                _, amt_raters, old_rating = line_extract(line)
                new_rating = round(((old_rating * amt_raters + rating) / (amt_raters + 1)), 1)

                new_line = filename + " " + str(amt_raters + 1) + " " + str(new_rating) + "\n"
                lines[i] = new_line

                text.seek(0)
                text.truncate()
                text.writelines(lines)

                break

    if not line_written:
        with open(text_doc, "a") as text:
            new_line = filename + " 1 " + str(rating) + "\n"
            text.write(new_line)

# Extracts the current data from a line (returns filename, amt_raters, rating)
def line_extract(line):
    line = line.replace("\n", "")
    split_line = line.split()
    filename = split_line[0]
    amt_raters = int(split_line[1])
    rating = float(split_line[2])
    return filename, amt_raters, rating

# Gets the rating of the current image
def get_current_rating(filename):
    text_doc = "temp_ratings.txt"
    with open(text_doc, "r") as text:
        lines = text.readlines()
        for line in lines:
            potential_filename, _, rating = line_extract(line)
            if filename == potential_filename:
                return rating
            else:
                continue

        return "You are first to rate this person!"


if __name__ == '__main__':
    app.run(debug=True)