from mtcnn import MTCNN
import PIL
import matplotlib.pyplot as plt
import pathlib
import numpy as np
import pandas as pd
from oursql import create_db_connection, add_name, edit_name
from my_creds import SQL_Creds
import os

credentials = SQL_Creds()

db = "tentonone"
db_connection = create_db_connection(credentials.host, credentials.username, credentials.passwd, db)

def process_image(impath, percent_margin=0.25):
    img = PIL.Image.open(impath)
    img = img.convert("RGB")
    pixels = np.array(img)
        
    detector = MTCNN()
    face = detector.detect_faces(pixels)

    box = face[0]["box"]

    margin = box[3] * percent_margin

    # Original Face Shape
    x = max(box[0] - margin, 0)
    y = max(box[1] - margin, 0)
    width = min(box[2] + 2 * margin, img.width - x)
    height = min(box[3] + 2 * margin, img.height - y)

    center = (x + (width / 2), y + (height / 2))

    # Make Image Square
    x = center[0] - (height / 2)
    y = center[1] - (height / 2)
    right = x + height
    bottom = y + height

    cropped_img = img.crop((x, y, right, bottom))
    resized_image = cropped_img.resize((600, 600))
    return resized_image

def load_image_into_1020(unedited_image_path, category):
    unedited_image_path = str(unedited_image_path)

    # Checking if the image is already on 1020
    all_images = list(pathlib.Path("images/").glob("*/*.jpg"))
    all_images = [os.path.basename(name) for name in all_images]
    filename = os.path.basename(unedited_image_path)
    if filename in all_images:
        print("Image already on Ten to None.")
        return True

    # Steps for Success:
    # 1. Find the image info in images.csv
    # 2. Crop Image
    # 3. Save image in men folder on 1020
    # 4. Add a row to names table
    # 5. Profit

    # Step 1: Get image info from images.csv
    df = pd.read_csv("images.csv", header=None)
    filename = unedited_image_path[::-1][:unedited_image_path[::-1].index("/")][::-1]
    try:
        row = df[df[1] == filename].values[0]
    except:
        print(f"{filename} not added to images.csv yet.")
        return False
    
    # Row[1] is filename and Row[4] is categories
    name, _, og_filename, source, _ = row

    # Step 4: Adding the name to the names table
    result = add_name(db_connection, name, category, filename, og_filename, source)
    if result == False:
        print(f"Error: was not able to add {name} to Ten to None")
        return False

    # Step 2: Crop Image
    final_image = process_image(unedited_image_path)

    # Step 3: Save image in men folder on 1020
    final_image.save(f"images/{category}/{filename}")

    # Step 5:
    print(f"{name} successfully added to Ten to None.")
    return True

def replace_image(unedited_image_path, category):
    try:
        new_image = process_image(unedited_image_path)
        filename = os.path.basename(unedited_image_path)
        new_image.save(f"images/{category}/{filename}")
        print(f"{filename} has been replaced.")
    except:
        return False
    return True

if __name__ == "__main__":
    bad_people = []

    '''
    unedited_men = list(pathlib.Path("/home/ethan/Pictures/unedited_photos/men/").glob("*.jpg"))
    for man in unedited_men:
        result = load_image_into_1020(man, "men")
        if result == False:
            bad_people.append(man)
    print("All done with the men!")
    '''

    '''
    unedited_women = list(pathlib.Path("/home/ethan/Pictures/unedited_photos/women/").glob("*.jpg"))
    for woman in unedited_women:
        result = load_image_into_1020(woman, "women")
        if result == False:
            bad_people.append(woman)
    print("All done with the women!")
    

    print("Here are the bad apples: ")
    for apple in bad_people:
        print(apple) 
    '''
    
    #edit_name(db_connection, original_name="LilyPichu", new_gender="women")
    
    print("All done!")
        
    