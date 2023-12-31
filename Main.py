import csv
import gc
import hashlib
import re
import time

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


@jit
def convert(seconds):
    day = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return day, hour, minutes, seconds


def load_last_attempt():
    with open('Untested_links', 'r') as file:
        first_line = file.readline().strip()
    return first_line


def delete_first_line(file_path):
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        lines = list(csv_reader)

    # Check if the file has at least one line
    if not lines:
        print("File is empty. Generate new codes.")
        return

    # Overwrite the file with the content starting from the second line
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(lines[1:])


def current_attempt(last_code):
    with open('Untested_links', 'r', encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if last_code in line:
                return line_num + 1


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


@jit(forceobj=True)
def check_image_hashes(hashed_image):
    return hashed_image not in hashes


def count_lines():
    with open('Untested_links', 'r') as file:
        line_count = sum(1 for _ in file)
    return line_count


def status(counter, exect_times, link_counter):
    print('--------------------')
    lines_left = count_lines()

    average_attempt = round((sum(exect_times) / len(exect_times)), 4)
    sec_till_done = (lines_left - 1) / average_attempt
    chance_link = round((link_counter / counter) * 100, 4)
    day, hour, minutes, seconds = convert(sec_till_done)

    print('Average attempt time:', average_attempt, 'sec(s).')
    print('Percent chance link found:', chance_link, '%')
    print('Time remaining:', "%d day(s) %02d:%02d:%02d" % (day, hour, minutes, seconds))
    print('--------------------')


def main():
    counter = 1
    link_counter = 0
    exect_times = []

    last_code = load_last_attempt()
    start_line = current_attempt(last_code)

    print('   ---STATUS---')
    print('Last code checked:', last_code)
    print('--------------------')

    with open('Untested_links', 'r', encoding="utf-8") as file:
        for i, attempt in enumerate(file):
            start = time.perf_counter()

            if i >= start_line:
                attempt = str(attempt).strip()
                link = header + attempt

                try:
                    if request_picture_data(link):
                        with open(out_path, "rb") as f:
                            image_hash = (hashlib.sha256(f.read()).hexdigest())

                        if check_image_hashes(image_hash):
                            with open("Codes.csv", 'a', newline='') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow([attempt, link])

                            link_counter += 1
                except Exception as e:
                    print(e)

            end = time.perf_counter()
            exect_times.append((end - start))

            delete_first_line('Untested_links')

            if counter % 50 == 0:
                print('   ---STATUS---')
                print('Last code checked:', attempt)
                print('Total attempts:', counter, '\nTotal links found:', link_counter)
                status(counter, exect_times, link_counter)

            counter += 1


if __name__ == "__main__":
    gc.enable()
    main()
