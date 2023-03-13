import moviepy.editor as mp
import os
import cv2
import shutil
import time
import pygame
import math
import re

def vidToAud(file):
    clip = mp.VideoFileClip("./" + file)
    clip.audio.write_audiofile("./" + file.split(".")[0] + ".mp3")

def extractImages(pathIn, pathOut, length, width):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    while True:
        success, image = vidcap.read()
        if success:
            aspectR = image.shape[0]/image.shape[1]
            height = int(width*aspectR)
            dim = (width, height)
            resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            percent = (int(count)/int(length))*100
            print("  Converting frames... " + math.floor(percent)*"#" + (100 - math.floor(percent))*" " + str(round(percent, 2)) + "%" + " " + str(int(count)) + "/" + str(int(length)), end="\r")
            cv2.imwrite(pathOut + "\\frame%d.jpg" % count, resized)
            count = count + 1
        else:
            print("\nFrames done!")
            break

def sound(mp3File):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(f'./saves/{mp3File}')
        pygame.mixer.music.play()
    except Exception:
        print("no audio")

def createAnimation(mp4File, mp3File, length, fps):

    shutil.copyfile(f"./{mp3File}", f"./saves/{mp3File}")
    os.remove(f"./{mp3File}")

    frameN = 5

    sample = cv2.imread(f"./frames/frame0.jpg")

    h = sample.shape[0]
    w = sample.shape[1]

    lastAsciiFrame = ((w*"p") + "\n")*h

    txtFile = mp4File.split(".")[0] + ".txt"

    if not os.path.isdir("./saves"):
        os.makedirs("./saves")

    if os.path.isfile(f"./saves/{txtFile}"):
        input(f"{txtFile} will overwrite, is that ok? ENTER to accept control+C to stop program")
    
    with open("./saves/" + txtFile, "w+") as file:
        file.write(str(w) + " " + str(h) + " " + str(fps) + "\n|")
        while os.path.isfile(f"./frames/frame{frameN}.jpg"):
            asciiFrame = ""
            try:
                frame = cv2.imread(f"./frames/frame{frameN}.jpg")
                for y in range(h):
                    line = ""
                    for x in range(w):
                        if (int(frame[y, x][0]) + int(frame[y, x][1]) + int(frame[y, x][2]))/3 >= 204:
                            line += "@"
                        elif (int(frame[y, x][0]) + int(frame[y, x][1]) + int(frame[y, x][2]))/3 >= 153:
                            line += "#"
                        elif (int(frame[y, x][0]) + int(frame[y, x][1]) + int(frame[y, x][2]))/3 >= 102:
                            line += "l"
                        elif (int(frame[y, x][0]) + int(frame[y, x][1]) + int(frame[y, x][2]))/3 >= 51:
                            line += "."
                        else:
                            line += " "
                    asciiFrame += line + "\n"
                percent = (int(frameN)/int(length))*100
                print("  Creating animation file... " + math.floor(percent)*"#" + (100 - math.floor(percent))*" " + str(round(percent, 2)) + "%" + " " + str(int(frameN)) + "/" + str(int(length)), end="\r")
                for i, char in enumerate(asciiFrame):
                    if char != lastAsciiFrame[i]:
                        file.write(f"{i}={char}\n")
                lastAsciiFrame = asciiFrame

                frameN += 1
                file.write("n\n")
            except KeyboardInterrupt:
                break
        print("\n---\nDone!\n---")
        cleanUp(True)

def cleanUp(prompt):

    if prompt:
        if input("clean-up? (y/n): ") != "y":
            return
        shutil.rmtree("./frames")

def startup():
    os.system('cls')
    usrIn = input(f"What to do?\n\"p\": load and play a video\n\"c\": create a video file to play\n\"clean\": clean-up\n--> ")
    if usrIn == "p":
        play()
    elif usrIn == "c":
        create()
    elif usrIn == "clean":
        cleanUp(True)
    else:
        print("\ninvalid option\n")
        startup()

def create():
    files = os.listdir("./")

    possibilities = []

    for i in files:
        if i.split(".")[-1] == "mp4":
            possibilities.append(i)

    for i, n in enumerate(possibilities):
        print(i, "for", n)
    usrIn = input(f"What file do you want to use?: ")
    try:
        mp4File = possibilities[int(usrIn)]
    except:
        print("invalid input:", usrIn)
        exit()

    width = int(input("Width?--> "))

    mp3File = mp4File.split(".")[0] + ".mp3"

    vidToAud(mp4File)

    if not os.path.isdir("./frames"):
        os.makedirs("./frames")
    sample = cv2.VideoCapture(mp4File)
    length = int(sample.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = sample.get(cv2.CAP_PROP_FPS)
    extractImages(mp4File, "./frames", length, width)

    createAnimation(mp4File, mp3File, length, fps)

    cleanUp(False)

def play():
    files = os.listdir("./saves")
    options = []
    for file in files:
        if file.split(".")[-1] == "txt":
            options.append(file.split(".")[:-1])
    
    for i, option in enumerate(options):
        print(i, "for", option)

    try:
        sourceFile = options[int(input("Choose one\n--> "))]
    except:
        play()

    with open("./saves/" + sourceFile[0] + ".txt") as file:
        text = file.read()
    info = text.split("\n")[0]
    fps = float(info.split(" ")[2])
    w = int(info.split(" ")[0])
    h = int(info.split(" ")[1])

    frames = text.split("|")[1].split("n\n")

    millisecondsPF = round(1 / fps, 4)

    os.system('cls')
    print("\n" + h * (w * "aa" + "\n"))
    input("Resize your window. Press enter to start...")
    os.system('cls')

    frame = h * (w * "#" + "\n")
    sound(sourceFile[0] + ".mp3")
    try:
        nextFrame = time.time() + millisecondsPF
        for current in frames:
            if nextFrame + millisecondsPF < time.time():
                continue
            nextFrame += millisecondsPF
            frame = list(frame)
            for line in current.split("\n")[:-1]:
                frame[int(line.split("=")[0])] = line.split("=")[1]
            frame = "".join(frame)
                    
            print((h + 2)*"\033[F")
            print(re.sub(r"([^\n])", r"\1\1", frame, flags=re.MULTILINE))

            while time.time() < nextFrame:
                pass
    except KeyboardInterrupt:
            exit()
    startup()

if __name__ == "__main__":
    startup()

    print("exit")
