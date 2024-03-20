from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
import os
import pathlib
import random
from oursql import *
from send_email import send_email
from urllib.parse import unquote
from datetime import datetime

app = Flask(__name__)
amt_unique = 150

all_men_images = list(pathlib.Path("/home/ethangomez/tentonone/images").glob("men/*.jpg"))
all_men_images = [str(filepath) for filepath in all_men_images]

all_women_images = list(pathlib.Path("/home/ethangomez/tentonone/images").glob("women/*.jpg"))
all_women_images = [str(filepath) for filepath in all_women_images]

db = "ethangomez$tentonone"
db_connection = create_db_connection(credentials.host, credentials.username, credentials.passwd, db)
db_connection = guarantee_db_connection(db_connection)

@app.route('/')
def index():
    return render_template('index.html')

# Serve images in the /images directory
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

# Serve icon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('images', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Begins the game by loading the game template and providing the first image
@app.route('/rate')
def rate():
    return render_template("rate.html")

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

# Provides the Javascript function with a random image
@app.route("/get_image", methods=["POST"])
def get_image():
    data = request.get_json()
    gender_choice = data["gender_choice"]
    sessionID = data["sessionID"]
    if sessionID:
        if len(sessionID) > 30:
            sessionID = sessionID[:30]

    image_path = get_random_image(gender_choice, sessionID)

    name, source = get_name(image_path)
    source_type = determine_source_type(source)
    #print(name)

    result = {"impath" : image_path, "name" : name, "source" : source, "source_type" : source_type}

    return jsonify(result=result)

# Recieves the rating, amt_raters, ranking from the submit button
@app.route("/send_rating", methods=["POST"])
def send_rating():
    data = request.get_json()

    link = data["image_path"]
    filename = unquote(extract_filepath(link))

    rating = float(data["slider_value"])

    try:
        sessionID = data["sessionID"]
        if sessionID:
            if len(sessionID) > 30:
                sessionID = sessionID[:30]
    except:
        sessionID = "erroredID"

    global db_connection
    db_connection = guarantee_db_connection(db_connection)

    if rating > 10 or rating < 0:
        pass
    else:
        add_rating(db_connection, sessionID, filename, rating)
        
    rating_now = clean_num(get_current_rating(db_connection, filename))
    #rating_now = 5.5

    if rating_now == -1:
        rating_now = "[Error, please report this to us]"

    amt_raters = get_count(db_connection, filename)
    #amt_raters = 5
    ranking = get_ranking(db_connection, filename)
    #ranking = 1

    result = {"rating" : rating_now, "amt_raters" : amt_raters, "ranking" : ranking}

    return jsonify(result=result)

@app.route("/retrieve_ratings")
def retrieve_the_ratings():
    rankings = get_filtered_lines()
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

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# Define a route to generate the sitemap.xml dynamically
@app.route('/sitemap.xml')
def sitemap():
    # Generate the XML content dynamically based on your routes
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>{request.url_root}</loc>
            <changefreq>monthly</changefreq>
        </url>
        <url>
            <loc>{request.url_root + 'rate'}</loc>
            <lastmod>daily</lastmod>
        </url>
        <url>
            <loc>{request.url_root + 'leaderboard'}</loc>
            <lastmod>daily</lastmod>
        </url>
        <url>
            <loc>{request.url_root + 'about'}</loc>
            <lastmod>monthly</lastmod>
        </url>
        <url>
            <loc>{request.url_root + 'contact'}</loc>
            <lastmod>monthly</lastmod>
        </url>
    </urlset>"""

    # Create a response with the XML content
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml'

    return response

# Retrieves a random image path from the images directory
def get_random_image(gender_choice, sessionID):
    # Clearing last images from choices of men and women
    #print(f"Session ID: {sessionID}")
    if sessionID != None:
        #print("Session ID Was NOT None")
        past_images_query = f"SELECT DISTINCT filename FROM ratings WHERE sessionID = '{sessionID}';"

        global db_connection
        db_connection = guarantee_db_connection(db_connection)

        past_images = read_query(db_connection, past_images_query)
        past_images = [image[0] for image in past_images]
        #print(f"Past images: {past_images}")

        #print(f"All men images: {all_men_images}")

        rated_men = [("/home/ethangomez/tentonone/" + filename) for filename in past_images if ("/home/ethangomez/tentonone/" + filename) in all_men_images]
        if len(rated_men) > amt_unique:
            rated_men = rated_men[-amt_unique:]
        rated_women = [("/home/ethangomez/tentonone/" + filename) for filename in past_images if ("/home/ethangomez/tentonone/" + filename) in all_women_images]
        if len(rated_women) > amt_unique:
            rated_women = rated_women[-amt_unique:]

        unrated_men = list(set(all_men_images) - set(rated_men))
        unrated_women = list(set(all_women_images) - set(rated_women))

        #print(f"Rated men: {rated_men}")
        #print(f"Rated women: {rated_women}")
        #print(f"length of unrated men: {len(unrated_men)}")
        #print(f"length of unrated women: {len(unrated_women)}")
    else:
        #print("Session ID WAS NONE!!!!!!!!!!!!")
        #print("NOT PRINTING RATED MEN / WOMEN")
        unrated_men = all_men_images
        unrated_women = all_women_images

    if gender_choice == "men":
        random_impath = random.choice(unrated_men)

    elif gender_choice == "women":
        random_impath = random.choice(unrated_women)

    else: # When gender_choice == "both" or any other circumstance
        all_images = unrated_men + unrated_women
        random_impath = random.choice(all_images)

    # Test individual person
    #chosen_image = "images/men/Shaquille_O'Neal.jpg"

    chosen_image = extract_filepath(random_impath)
    return chosen_image

# Cleans floats so that there are no unnecessary digits on the leaderboard
def clean_num(num):
    to_clean = list(str(num))[::-1]

    # Limit the length of num
    if len(to_clean) > 7:
        to_clean = to_clean[::-1][:7][::-1]

    if (num == 10):
        return 10
    
    for i, number in enumerate(to_clean):
        if to_clean[i+2] == "." or to_clean[i+2] != number:
            if int(number) >= 5:
                to_clean[i] = str(int(number) + 1)
            else:
                to_clean[i] = number
            break

        if to_clean[i+1] != number:
            break
        else:
            to_clean[i] = ""

    return float("".join(to_clean[::-1]))

def get_filtered_lines():
    global db_connection
    db_connection = guarantee_db_connection(db_connection)

    ratings = get_all_average_ratings(db_connection)
    #ratings = [(0, 0, 0, 0, 0, 0)]
    ratings = sorted(ratings, key=(lambda x : x[2]))[::-1]

    for i, rating in enumerate(ratings):
        rating = list(rating)
        rating[2] = clean_num(rating[2])
        name, source = get_name(rating[0])
        rating.append(name)
        rating.append(source)
        rating.append(determine_source_type(source))
        ratings[i] = tuple(rating)

    return ratings

def extract_filepath(filepath):
    index = filepath.index("images")
    return filepath[index:]

# Also gets source. Just keep the name the same to confuse you in the future lol.
def get_name(impath):
    global db_connection
    db_connection = guarantee_db_connection(db_connection)

    filename = os.path.basename(impath).strip()
    filename = unquote(filename)
    results = get_individual_info(db_connection, filename)[0]
    #results = (10, "John", 0, 0, 0, "yourmom.com")
    _, name, _, _, _, source = results
    name = unquote(name)
    #print("Getting name for...", name)

    return name, source

# Determines the type of the source so that I can link it correctly on the site.
def determine_source_type(source):
    if source[0] == "<":
        return "wiki"
    elif source[:4] == "http" or source[:3] == "www":
        return "link"
    else:
        return "other"

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
    #print("Running!")
    #print(get_random_image(gender_choice))
