import csv
import itertools
import string


def iterator(charset, length_of_codes):
    return (''.join(candidate)
            for candidate in itertools.product(charset, repeat=length_of_codes))


chars = string.ascii_lowercase + string.digits
code_length = 5

codes_generator = iterator(chars, code_length)

with open('Test.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    for code in codes_generator:
        if not code.isdigit():  # Check if the code is not a number
            csv_writer.writerow([code])
