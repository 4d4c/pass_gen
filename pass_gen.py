from sys import stdout
from uuid import uuid4
from os import remove
from itertools import product
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from multiprocessing.pool import ThreadPool

l33t = {
    'a': ['a', 'A', '@', '4'],
    'b': ['b', 'B', '8', '6'],
    'c': ['c', 'C', '[', '{', '(', '<'],
    'd': ['d', 'D', ],
    'e': ['e', 'E', '3'],
    'f': ['f', 'F'],
    'g': ['g', 'G', '6', '9'],
    'h': ['h', 'H', '#'],
    'i': ['i', 'I', '1', 'l', 'L', '|', '!'],
    'j': ['j', 'J'],
    'k': ['k', 'K'],
    'l': ['l', 'L', 'i', 'I', '|', '!', '1'],
    'm': ['m', 'M'],
    'n': ['n', 'N'],
    'o': ['o', 'O', '0', 'Q'],
    'p': ['p', 'P'],
    'q': ['q', 'Q', '9', '0', 'O'],
    'r': ['r', 'R'],
    's': ['s', 'S', '$', '5'],
    't': ['t', 'T', '+', '7'],
    'u': ['u', 'U', 'v', 'V'],
    'v': ['v', 'V', 'u', 'U'],
    'w': ['w', 'W'],
    'x': ['x', 'X', '+'],
    'y': ['y', 'Y'],
    'z': ['z', 'Z', '2'],
}


def get_keyword_templates(keyword, simple):
    letters = []

    # Use only lower/upper case letters
    if simple:
        for letter in keyword:
            if letter in l33t.keys():
                letters.append([letter, letter.upper()])
            else:
                letters.append(letter)
    # Use whole l33t list
    else:
        for letter in keyword:
            if letter in l33t.keys():
                letters.append(l33t[letter])
            else:
                letters.append(letter)

    return product(*letters)


def get_crunch_templates(keyword, length):
    # Get all combinations for crunch patterns
    repeat = length - len(keyword)
    return list(product("@,%^", repeat=repeat))


def run_crunch(pattern, lenght, out_filename, index, len_crunch_patterns):
    tmp_out_filename = str(uuid4()) + "_" + out_filename

    # Print progress output on the same line
    stdout.write("[{0: >3}%] Processing pattern {1} out of {2}...                    \r".format(index * 100 / len_crunch_patterns, index, len_crunch_patterns))
    stdout.flush()

    command = "crunch {0} {0} -t '{1}' -o {2} 2>/dev/null".format(lenght, pattern, tmp_out_filename)
    process = Popen(command, shell=True, stdout=PIPE)
    process.wait()

    with open(out_filename, "a") as out_file, open(tmp_out_filename, "r") as tmp_out_file:
        out_file.write(tmp_out_file.read())

    remove(tmp_out_filename)


# Get script arguments
parser = ArgumentParser(description="Create different password combinations from keyword")
parser.add_argument("-k", "--keyword", required=True, type=str, action="store", dest="keyword", help="Keyword (part of password)")
parser.add_argument("-l", "--length", required=True, type=int, action="store", dest="lenght", help="Length of the password")
parser.add_argument("-s", "--simple", required=False, action="store_true", dest="simple", help="Use only simple pattern combinations (only upper and lower case letters in patterns)")
parser.add_argument("-t", "--threads", required=False, type=int, action="store", dest="threads", default=20, help="Crunch thread number")
parser.add_argument("-o", "--ouputfile", required=False, type=str, action="store", dest="out_filename", default="wordlist.txt", help="Output file name")
args = parser.parse_args()

keyword_templates = get_keyword_templates(args.keyword, args.simple)
crunch_templates = get_crunch_templates(args.keyword, args.lenght)

# Get patterns, which we will use for running crunch
crunch_patterns = []
for keyword_template in keyword_templates:
    for crunch_template in crunch_templates:
        for index in range(0, len(crunch_template) + 1):
            crunch_patterns.append("".join(crunch_template)[:index] + "".join(keyword_template) + "".join(crunch_template)[index:])

pool = ThreadPool(args.threads)

# Run thread pool
len_crunch_patterns = len(crunch_patterns)
for index, crunch_pattern in enumerate(crunch_patterns):
    pool.apply_async(run_crunch, (crunch_pattern, args.lenght, args.out_filename, index, len_crunch_patterns))

pool.close()
pool.join()

print
