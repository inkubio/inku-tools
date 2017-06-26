import numpy as np
import cv2
from PIL import Image
import os


def cv2pil(cv2_img):
    # Convert the cv image to a PIL image
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv2_img)


def detectFace(img, classifier):
    # Finds faces in grayscale images
    faces = classifier.detectMultiScale(img, 1.3, 5)
    for (x, y, w, h) in faces:
        return (x, y, w, h)
        # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)


def crop_image(img, x, y, width):
    # Crops a PIL image
    topleft_x = x - width
    topleft_y = y - width if y - width > 0 else 0
    bottomright_x = x + width * 2
    bottomright_y = y + width * 2 if y + width * 2 < img.size[1] else img.size[1]

    cropped = img.crop(
        (topleft_x,
         topleft_y,
         bottomright_x,
         bottomright_y)
    )
    return cropped


def resize(img, size):
    # Resizes img in place to a square with side length of size
    size = (size, size)
    img.thumbnail(size, Image.ANTIALIAS)


def main():
    folder = input("Path to images: ")
    savefolder = input("Folder to save to: ")

    filepaths = set()
    for root, dirs, files in os.walk(folder):
        for filename in files:
            filepaths.add(os.path.join(folder, filename))

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    for file in filepaths:
        img = cv2.imread(file)
        pil_img = cv2pil(img)
        gs_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        area = detectFace(gs_img, face_cascade)
        cropped = crop_image(pil_img, area[0], area[1], area[2])
        resize(cropped, 512)

        # Show image to user and ask for name
        cropped.show()
        person = input("Who is this: ")
        filename = "_".join(person.split()) + ".jpg"
        cropped.save(os.path.join(savefolder, filename))

        # Close shown image
        os.system('killall display')

main()
