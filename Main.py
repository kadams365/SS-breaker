import csv
import gc
import hashlib
import os
import random
import re
import shutil
import string
from time import sleep

import pygame
import requests
from PIL import Image
from bs4 import BeautifulSoup

header = "https://prnt.sc/"
screen = pygame.display.set_mode([1000, 720])
color = (0, 0, 0)

sound = r"\SS Breaker\PhotoFound.mp3"
out_path = r'\SS_Breaker\Temp1.png'
holding = r'\SS_Breaker\SS'
old_temp = ""


def generate_code():
    while True:
        length = random.randint(4, 9)
        result = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(length))
        result.strip()

        if result.isdigit():
            generate_code()

        # Checking to see if code has been checked before
        with open("CodesV4.csv", 'r') as csvfile:
            reader = csv.reader(csvfile)

            # If code is already in file get a new code
            if result not in reader:
                break

    with open("CodesV4.csv", 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([result])

    return result


def request_picture_data(link):
    with requests.Session() as s:
        r = s.get(link, headers={'User-Agent': 'Chrome'})
        soup = BeautifulSoup(r.content, "html.parser")
        picture_data = str(soup.find(id="screenshot-image")).strip()

        picture_string = str(re.findall(r'(https?://\S+)', picture_data)).strip()
        picture_link = picture_string.translate({ord(c): None for c in "[]\'\">"}).strip()

        #   Error when code generation creation is not a valid image link.
        if picture_data == "None":
            return
        elif r.url == header:
            return
        elif not picture_link:
            return
        else:
            response = s.get(picture_link[:-1], headers={'User-Agent': 'Chrome'})
            with open(out_path, 'wb') as f:
                f.write(response.content)


def main(oldtemp):
    code = generate_code()
    link = header + code
    pic_file = code + '.png'

    request_picture_data(link)

    with open(out_path, "rb") as file:
        temp = hashlib.sha256(file.read()).hexdigest()

    if hash1 != temp and hash2 != temp:
        if oldtemp == temp:
            main(oldtemp)

        oldtemp = temp

        try:
            img = pygame.image.load(out_path).convert()
        except Exception:
            main(oldtemp)

        image = Image.open('Temp1.png')
        image.save('Temp1.png', optimize=True, quality=25)
        image.close()

        shutil.copy(out_path, holding)
        os.rename(holding + '\\' + out_path, pic_file)
        shutil.move(pic_file, holding)

        screen.fill(color)
        pygame.display.flip()

        print("New link:", link)

        pygame.event.pump()
        screen.blit(img, (0, 0))
        pygame.display.flip()
        sleep(1)
        main(oldtemp)
    else:
        main(oldtemp)


gc.enable()
main(old_temp)
