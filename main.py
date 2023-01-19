import moviepy.editor as mp
import os
import cv2
from PIL import Image
import shutil
import time
import pygame

fps = 30

millisecondsPF = round(1 / fps, 3)

print(millisecondsPF)

def vidToAud(file):
    clip = mp.VideoFileClip("./" + file)
    clip.audio.write_audiofile("./" + file.split(".")[0] + ".mp3")

def extractImages(pathIn, pathOut):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    while True:
        success, image = vidcap.read()
        if success:
            aspectR = image.shape[0]/image.shape[1]
            width = 100
            height = int(100*aspectR)
            dim = (width, height)
            resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            ret, bw = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)
            print ('Saved Frame!', count)
            cv2.imwrite(pathOut + "\\frame%d.jpg" % count, bw)
            count = count + 1
        else:
            print("Frames done!")
            break

def sound():
    pygame.mixer.init()
    mp3FileDir = os.path.dirname(__file__) + "/" + mp3File
    if not os.path.isdir("./cache"):
        os.makedirs("./cache")
    shutil.copyfile(mp3FileDir, './cache/audCache.mp3')
    pygame.mixer.music.load('./cache/audCache.mp3')
    pygame.mixer.music.play()

def animation():
    frameN = 5

    sample = cv2.imread(f"./frames/frame0.jpg")

    h = sample.shape[0]
    w = sample.shape[1]

    while os.path.isfile(f"./frames/frame{frameN}.jpg"):
        nextFrame = time.time() + millisecondsPF
        frame = cv2.imread(f"./frames/frame{frameN}.jpg")
        asciiFrame = ""
        for y in range(h):
            line = "\n"
            for x in range(w):
                if frame[y, x][0] >= 180:
                    line += "  "
                else:
                    line += "##"
            asciiFrame += line
        print(asciiFrame)
        frameN += 1
        while time.time() < nextFrame:
            pass

if __name__ == "__main__":
    files = os.listdir("./")

    for i in files:
        if i.split(".")[-1] == "mp4":
            mp4File = i
            break

    mp3File = mp4File.split(".")[0] + ".mp3"

    if mp3File in files:
        print("Audio found!")
    else:
        vidToAud(mp4File)

    if not os.path.isdir("./frames"):
        os.makedirs("./frames")
        extractImages(mp4File, "./frames")
    else:
        print("Frames found!")

    input("Press enter to start...")

    sound()
    animation()

    if input("clean-up? (y/n): ") == "y":
        shutil.rmtree("./frames")
        time.sleep(1)
        os.remove(f"./{mp3File}")

    print("Exit")
