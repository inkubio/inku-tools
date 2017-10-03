import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk
import os


class GUI:
    def __init__(self, master):
        # GUI and main functionality
        self.filepaths = []
        self.skipped = []
        self.index = 0
        self.set_length = 0
        self.img = None
        self.cropped = None
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        self.master = master
        master.title("NaamaRaja")

        tk.Label(master, text="Input path: ").grid(row=0, sticky=tk.E)
        tk.Label(master, text="Output path: ").grid(row=1, sticky=tk.E)

        # Input and output folders
        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1, sticky=tk.W)
        self.input_entry.insert(0, "test")
        self.output_entry = tk.Entry(master)
        self.output_entry.grid(row=1, column=1, sticky=tk.W)
        self.output_entry.insert(0, "out")

        # Canvas for pictures
        self.canvas = tk.Canvas(master, width=512, height=512)
        self.canvas.grid(row=3, columnspan=2)

        # Entry for name of person in picture
        tk.Label(master, text="Name of person: ").grid(row=4, sticky=tk.E)
        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=4, column=1, sticky=tk.W)

        # Control buttons
        self.start_button = tk.Button(master, text="Start", command=self.start)
        self.start_button.grid(row=5)
        self.next_button = tk.Button(master, text="Next picture", command=self.next)
        self.next_button.grid(row=5, column=1)

        self.status_label = tk.Label(master, text="Welcome to NaamaRaja.")
        self.status_label.grid(row=6, columnspan=2)

        # Key bindings
        self.start_button.bind("<Return>", self.start)
        self.name_entry.bind("<Return>", self.next)
        self.start_button.focus()

    def _cv2pil(self, cv2_img):
        # Convert the OpenCV image to a PIL image
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_img)

    def _detectFace(self, img, classifier):
        # Finds faces in grayscale OpenCV images
        faces = classifier.detectMultiScale(img, 1.3, 5)
        for (x, y, w, h) in faces:
            return (x, y, w, h)
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    def _crop_image(self, img, x, y, width):
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

    def _resize(self, img, size):
        # Resizes PIL image in place to a square with side length of size
        size = (size, size)
        img.thumbnail(size, Image.ANTIALIAS)

    def _show_image(self):
        # Analyze, crop and show the next image
        img = cv2.imread(self.filepaths[self.index])
        self.status_label.config(text=self.filepaths[self.index])
        pil_img = self._cv2pil(img)
        gs_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.index += 1

        area = self._detectFace(gs_img, self.face_cascade)
        if not area:  # Couldn't find a face
            self.skipped.append(self.filepaths[self.index - 1])
            self.next()
            return

        self.cropped = self._crop_image(pil_img, area[0], area[1], area[2])
        self._resize(self.cropped, 512)
        self.img = image = ImageTk.PhotoImage(self.cropped)
        imagesprite = self.canvas.create_image(512, 512, image=image, anchor='se')
        self.name_entry.delete(0, tk.END)
        self.name_entry.focus()

    def start(self, event=None):
        # Initialize folders and pictures
        self.skipped = []

        folder = self.input_entry.get()
        savefolder = self.output_entry.get()

        filepaths = set()
        for root, dirs, files in os.walk(folder):  # Get relative paths to input files
            for filename in files:
                filepaths.add(os.path.join(folder, filename))

        self.filepaths = list(filepaths)
        self.set_length = len(self.filepaths)

        self._show_image()

    def next(self, event=None):
        # Show next picture to be renamed and cropped
        if self.index == self.set_length - 1:
            if self.skipped:
                print("Failed to find a face in following images:")
                for skip in self.skipped:
                    print(skip)
            self.status_label.config(text="All done.")
            return

        person = self.name_entry.get()
        if person.lower() in ["skip", "fail", "pass", "no", "none"]:
            self.skipped.append(self.filepaths[self.index - 1])
        else:
            filename = "_".join(person.split()) + ".jpg"
            self.cropped.save(os.path.join(self.output_entry.get(), filename))

        self._show_image()


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = GUI(root)
    root.mainloop()
