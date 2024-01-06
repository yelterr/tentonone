from mtcnn import MTCNN
import PIL
import matplotlib.pyplot as plt
import pathlib

def process_image(impath, margin=10):
    img = PIL.Image.open(impath)
    pixels = plt.imread(impath)

    detector = MTCNN()
    face = detector.detect_faces(pixels)

    box = face[0]["box"]

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
    resized_image = cropped_img.resize((500, 500))
    return resized_image

#img = process_image("static/images/affleck.jpg")
#img.save("static/images/affleck.jpg")

if __name__ == "__main__":
    custom_margin = 200

    image_dir = pathlib.Path("static/images/")
    all_images = list(image_dir.glob("*/*.jpg"))

    for impath in all_images:
        img = PIL.Image.open(impath)
        # If the image is a correctly sized square, it's already been cropped
        if img.size[0] == img.size[1] and img.size[0] == 500:
            continue
        # Anything else is not cropped.
        else:
            # Not cropped yet
            img = process_image(impath, custom_margin)
            img.save(impath)
            continue
