import os
import sys

from giftkey import gen_key
# gen_key(giftID, giftkey=key, count=1, servers=servers, channels=channels)

from yy.config.dump import read_file


def main(root):
    for root, _, files in os.walk(root):
        for file in files:
            if ".csv" in os.path.splitext(file):
                fullname = os.path.join(root, file)
                _, header, reader, _ = read_file(fullname)
                for line in reader:
                    info = dict(zip(header, line))
                    print info
                    gen_key(int(info["itemID"]), info["giftkey"], count=1)


if __name__ == "__main__":
    main(sys.argv[1])
