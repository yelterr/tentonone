from bs4 import BeautifulSoup
import requests
from PIL import Image
import time
import random

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}



def rand_sleep():
    random_integer = random.randrange(0, 5)
    time.sleep(random_integer)



def add_csv_row(name=None, my_filename=None, og_filename=None, source=None, gender=None):
    with open('images.csv','a') as fd:
        row = f"{name},{my_filename},{og_filename},{source},{gender},\n"
        fd.write(row)



def extract_image_link(small_image_url):
    try:
        split_index = small_image_url[::-1].index("xp")-1
    except:
        split_index = small_image_url[::-1].index("/")
    
    image_filename = small_image_url[::-1][:split_index][::-1].replace("%28", "(").replace("%29", ")")
    all_info_link = f"https://commons.wikimedia.org/wiki/File:{image_filename}"

    rand_sleep()
    response = requests.get(all_info_link, headers=headers)
    soup = BeautifulSoup(response.text, features="html.parser")

    # Get the image link
    links = soup.find_all("a")
    img_url = None
    for link in links:
        if link.get("class") == ["internal"]:
            img_url = link["href"]

    if img_url == None:
        return None, None, None

    # Get the source embed
    source_link = None
    source_name = None
    tds = soup.find_all("td")
    for i, td in enumerate(tds):
        if td.text == "Author":
            source_name = str(tds[i+1].text).strip()
            break
    
    if source_name != None:
        source_name = source_name.replace("\n", "").replace(",", "")
        source_embed = f'''<a href="{all_info_link}">{source_name}</a> <a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY-SA 3.0</a> via Wikimedia Commons'''
    else:
        source_embed = None

    return image_filename, img_url, source_embed



def download_image(name, category):
    search = "_".join(name.split())
    url = f"https://en.wikipedia.org/wiki/{search}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features="html.parser").find_all("td", class_="infobox-image")

        if soup:
            # Finally, download the image
            img_element = soup[0].find_all("img")[0]
            small_img_url = "http:" + str(img_element['src'])
            #print(small_img_url)
            og_filename, img_url, source_embed = extract_image_link(small_img_url)

            if img_url == None:
                print(f"Error: No image found for: {name}")
                add_csv_row(name=name, my_filename=None, og_filename=None, source=None, gender=category)
                return None
            
            print(og_filename)
            add_csv_row(name=name, my_filename=f"{search}.jpg", og_filename=og_filename, source=source_embed, gender=category)

            # TODO - Make these requests a bit more 'polite'? I mean wait a random amt of time beforehand to make the request.
            data = requests.get(img_url, headers=headers).content
            f = open(f'/home/ethan/Pictures/unedited_photos/{category}/{search}.jpg','wb') 
            f.write(data)
            f.close()

            # print(f"Image of {name} successfully downloaded.")
        else:
            print(f"Error: No image found for: {name}")
            add_csv_row(name=name, my_filename=None, og_filename=None, source=None, gender=category)
    else:
        print(f"Error: No image found for: {name}")
        add_csv_row(name=name, my_filename=None, og_filename=None, source=None, gender=category)

if __name__ == "__main__":

    # MEN images
    '''
    with open("/home/ethan/Desktop/men_names.txt") as men_txt:
        all_men = men_txt.readlines()
        for man in all_men:
            man = man.replace("\n", "")
            download_image(man, "men")
    '''
            
    # WOMEN images
    '''
    with open("/home/ethan/Desktop/women_names.txt") as women_txt:
        all_women = women_txt.readlines()
        for woman in all_women:
            woman = woman.replace("\n", "")
            download_image(woman, "women")
    '''