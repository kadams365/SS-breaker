import csv
import hashlib
import re
import string
from time import sleep

import requests
from bs4 import BeautifulSoup

header = "https://prnt.sc/"
out_path = '../Temp1.png'

hash1 = '157717479435656010a01c7af2836087675736f284355200b3492343f1de5f6a'
hash2 = '9b5936f4006146e4e1e9025b474c02863c0b5614132ad40db4b925a10e8bfbb9'
hash3 = '2d57ca272c43c543c7d0fe1f4965f834500a03d28543dace7c42cf47ed3932cb'
hash4 = '376f5045e4dd8bf68ac9e374518a01c18b2fdf76344f2cc08cac143acc4f3cb8'
hash5 = '64521da3e8bbdde2ef2b645c4468ba25c4dbbe07999f7fc74f763f4527f19a4f'

hashes = [hash1, hash2, hash3, hash4, hash5]

charset = string.ascii_lowercase + string.digits
base = len(charset)

# Create a mapping of characters to their respective values
char_to_value = {char: idx for idx, char in enumerate(charset)}
value_to_char = {idx: char for idx, char in enumerate(charset)}


def load_last_attempt():
    with open('Last_tested', 'r') as file:
        first_line = file.readline().strip()
    return first_line


def write_new_code(code):
    with open('Last_tested', 'w', newline='') as file:
        file.write(code)


def request_picture_data(link):
    with requests.Session() as s:
        r = s.get(link, headers={'User-Agent': 'Chrome'})
        soup = BeautifulSoup(r.content, "html.parser")
        picture_data = str(soup.find(id="screenshot-image")).strip()

        picture_string = str(re.findall(r'(https?://\S+)', picture_data)).strip()
        picture_link = picture_string.translate({ord(c): None for c in "[]\'\">"}).strip()

        if picture_data == "None" or r.url == header or not picture_link:
            return
        response = s.get(picture_link[:-1], headers={'User-Agent': 'Chrome'})
        with open(out_path, 'wb') as f:
            f.write(response.content)

        return True


# Function to increment the base-36 string
def increment_base36_string(s):
    s = list(s)  # Convert string to list to allow modification
    carry = 1  # Start with carry since we are incrementing

    for i in range(len(s) - 1, -1, -1):
        if carry == 0:
            break
        new_value = char_to_value[s[i]] + carry
        if new_value >= base:
            s[i] = charset[new_value % base]
            carry = new_value // base
        else:
            s[i] = charset[new_value]
            carry = 0

    if carry > 0:
        s.insert(0, charset[carry])

    return ''.join(s)


def check_image_hashes(hashed_image):
    return hashed_image not in hashes


def main():
    while True:
        last_code = load_last_attempt()
        attempt = last_code

        link = header + attempt

        try:
            if request_picture_data(link):
                with open(out_path, "rb") as f:
                    image_hash = (hashlib.sha256(f.read()).hexdigest())

                if check_image_hashes(image_hash):
                    with open("Codes.csv", 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([attempt, link])
                        print(link)
        except Exception as e:
            print(e)

        new_code = increment_base36_string(last_code)
        write_new_code(new_code)
        sleep(5)


if __name__ == '__main__':
    print("Starting...")
    main()
