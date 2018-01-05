# InkuTools

A command line tool for batch cropping and renaming pictures to be used on the Inkubio website. Crops to a centered picture of a persons face using OpenCV and PIL.

Dependencies in requirements.txt which can be installed quickly with "pip3 install -r requirements.txt". You might also need to install other packages as listed in req.txt

Upon executing naamaraja.py asks for the folder where lie pictures to be processed and the folder where to output the pictures. During runtime pictures are shown one by one and you will be prompted for a name in the command line. You should enter the first and last names of the person in question separated by a space, so the script will correctly name the output files as "first_last.jpg"

naamaraja-cli.py accepts two arguments: -i for path to input folder and -o for path to output folder. The script automatically crops all images in input folder and spits them out with the same filename into the output folder. Be advised, if you use the same folder for input and output your original files will be rewritten.