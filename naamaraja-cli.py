import numpy as np
import cv2
from PIL import Image, ImageTk
import os
import argparse
import traceback
from tqdm import tqdm
import face_recognition

class Processer:
    def __init__(self, in_folder, out_folder):
        # GUI and main functionality
        self.in_folder = in_folder
        self.out_folder = out_folder
        self.filepaths = []
        self.skipped = []
        self.index = 0
        self.set_length = 0
        self.img = None
        self.cropped = None
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    def _cv2pil(self, cv2_img):
        # Convert the OpenCV image to a PIL image
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_img)

    def _detectFace(self, img, classifier):
        # Finds faces in grayscale OpenCV images
        faces = classifier.detectMultiScale(img, 1.3, 5)
        for (x, y, w, h) in faces:
            return (x, y, w, h)

    def _detect_face(self, img):
        face_locations = face_recognition.face_locations(img)
        for face in face_locations:
            top, right, bottom, left = face
            return (left, top, bottom-top, right-left)



    def _crop_image(self, img, x, y, width):
        """ Crops a PIL image """
        center_y = y + int((width//2))
        center_x = x + int((width//2))

        # What are the ideal dimensions
        upper_length = int(1.5*width)
        lower_length = int(2.5*width)
        side_width = 2*width

        # Is there upper or lower limit on Y axis
        if center_y - upper_length < 0:
            upper_length = center_y
        if center_y + lower_length > img.size[1]:
            lower_length = img.size[1] - center_y

        # Is there left or right limit on X axis
        if center_x - side_width < 0:
            side_width = center_x
        if center_x + side_width > img.size[0]:
            side_width = img.size[0] - center_x

        # Get maximum side length
        max_height = upper_length + lower_length
        max_width = 2*side_width

        if max_width < max_height:
            max_side = max_width
            topleft_y = center_y - int((max_side//4)*1.5)
            bottomright_y = center_y + int((max_side//4)*2.5) + 2
            topleft_x = center_x - int(max_side//2)
            bottomright_x = center_x + int(max_side//2)
 
        else:
            max_side = max_height
            topleft_y = center_y - upper_length
            bottomright_y = center_y + lower_length
            topleft_x = center_x - int(max_side//2)
            bottomright_x = center_x + int(max_side//2)
        
        # Finally crop image
        cropped = img.crop(
            (topleft_x,
             topleft_y,
             bottomright_x,
             bottomright_y)
        )
        return cropped

    def _resize(self, img, size):
        # Resizes PIL image in place to a square with side length of size
        size = (size, size)
        img.thumbnail(size, Image.ANTIALIAS)

    def _show_image(self):
        # Analyze, crop and show the next image
        image = face_recognition.load_image_file(os.path.join(self.in_folder, self.filenames[self.index]))
        #img = cv2.imread( os.path.join(self.in_folder, self.filenames[self.index]))
        #pil_img = self._cv2pil(img)
        #gs_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.index += 1

        #area = self._detectFace(gs_img, self.face_cascade)
        area = self._detect_face(image)
        if not area:  # Couldn't find a face
            self.skipped.append(self.filenames[self.index - 1])
            return False
        
        pil_img = Image.fromarray(image)
        self.cropped = self._crop_image(pil_img, area[0], area[1], area[2])
        self._resize(self.cropped, 512)
        return True

    def start(self):
        # Initialize folders and pictures
        self.skipped = []
        self.index = 0


        filenames = set()
        for root, dirs, files in os.walk(self.in_folder):  # Get relative paths to input files
            for filename in files:
                filenames.add(filename)

        self.filenames = list(filenames)
        self.set_length = len(self.filenames)

        pbar = tqdm(total=self.set_length, unit="images")
        while self.index < self.set_length:
            try:
                pbar.set_postfix(file=self.filenames[self.index])
                self.next()
            except Exception as e:
                print(e)
                self.index += 1
            pbar.update(1)

        pbar.close()

        print("\nAll done.\n")
        if self.skipped:
            print("Failed to find a face in following images:")
            for skip in self.skipped:
                print(skip)


    def next(self):
        # Show next picture to be renamed and cropped
        if not self._show_image():
            return

        self.cropped.save(os.path.join(self.out_folder, self.filenames[self.index - 1]))





if __name__ == "__main__":
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i")
    parser.add_argument("-o")
    args = parser.parse_args()

    p = Processer(args.i, args.o)
    p.start()