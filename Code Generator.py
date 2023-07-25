from itertools import chain, product
import csv

chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
code_length = 5


def iterator(charset, length_of_codes):
    return (''.join(candidate)
            for candidate in chain.from_iterable(product(charset, repeat=i)
                                                 for i in range(length_of_codes, length_of_codes + 1)))


# Function to write generator object to a CSV file
def write_generator_to_csv(file_path, generator):
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        for row in generator:
            csv_writer.writerow(row)


write_generator_to_csv('Codes.csv', iterator(chars, code_length))
