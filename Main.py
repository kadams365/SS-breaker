import csv
import gc
import hashlib
import re
import time
from itertools import chain, product

import requests
from bs4 import BeautifulSoup
from numba import jit

header = "https://prnt.sc/"
out_path = 'Temp1.png'

hash1 = '157717479435656010a01c7af2836087675736f284355200b3492343f1de5f6a'
hash2 = '9b5936f4006146e4e1e9025b474c02863c0b5614132ad40db4b925a10e8bfbb9'
hash3 = '2d57ca272c43c543c7d0fe1f4965f834500a03d28543dace7c42cf47ed3932cb'
hash4 = '376f5045e4dd8bf68ac9e374518a01c18b2fdf76344f2cc08cac143acc4f3cb8'
hash5 = '64521da3e8bbdde2ef2b645c4468ba25c4dbbe07999f7fc74f763f4527f19a4f'

hashes = [hash1, hash2, hash3, hash4, hash5]
temp = ''

chars = 'abcdefghijklmnopqrstuvwxyz1234567890'


@jit
def convert(seconds, current_line, average_attempt):
    day = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return day, hour, minutes, seconds


def load_last_attempt():
    with open('last_code.txt', 'r') as f:
        line = f.readline()
        last_code = line.strip()

    return last_code


def save_last_attempt(last_code):
    with open('last_code.txt', 'w') as f:
        f.write(last_code + '\n')


def current_attempt(last_code):
    with open('Untested_links', 'r', encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if last_code in line:
                return line_num + 1


def iterator(charset, maxlength):
    return (''.join(candidate)
            for candidate in chain.from_iterable(product(charset, repeat=i)
                                                 for i in range(4, maxlength + 1)))


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

            return True


@jit(forceobj=True)
def check_image_hashes(hashed_image):
    if hashed_image not in hashes:
        return True

    return False


def status(counter, exect_times, link_counter, start_line):
    if counter % 250 == 0:
        print('--------------------')
        current_line = start_line + counter

        average_attempt = round((sum(exect_times) / len(exect_times)), 4)
        chance_link = round((link_counter / counter) * 100, 4)
        sec_till_done = (1501377 - current_line) / average_attempt
        day, hour, minutes, seconds = convert(sec_till_done, current_line, average_attempt)
        percent_comp = round((current_line / 1501377) * 100, 4)

        print('Average attempt time:', average_attempt, 'secs.')
        print('Percent chance link found:', chance_link, '%')
        print('Time remaining:', "%d day(s) %02d:%02d:%02d" % (day, hour, minutes, seconds))
        print('Percent complete:', percent_comp, '%')
        print('--------------------')


def main():
    counter = 1
    link_counter = 0
    exect_times = []

    last_code = load_last_attempt()
    start_line = current_attempt(last_code)

    print('   ---STATUS---')
    print('Last code checked:', last_code)
    print('Current line:', start_line + counter)

    with open('Untested_links', 'r', encoding="utf-8") as file:
        for i, attempt in enumerate(file):
            if i >= start_line:
                start = time.perf_counter()
                attempt = str(attempt).strip()

                save_last_attempt(attempt)

                if not attempt.isdigit():
                    link = header + attempt

                    try:
                        if request_picture_data(link):
                            with open(out_path, "rb") as f:
                                image_hash = (hashlib.sha256(f.read()).hexdigest())

                            if check_image_hashes(image_hash):
                                with open("CodesV4.csv", 'a', newline='') as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerow([attempt, link])

                                link_counter += 1
                    except Exception as e:
                        print(e)

                end = time.perf_counter()
                exect_times.append((end - start))

                if counter % 500 == 0:
                    print('   ---STATUS---')
                    print('Last code checked:', attempt)
                    print('Current line:', start_line + counter)
                    print('Total attempts:', counter, '\nTotal links found:', link_counter)
                    status(counter, exect_times, link_counter, start_line)

                counter += 1


if __name__ == "__main__":
    gc.enable()
    main()
