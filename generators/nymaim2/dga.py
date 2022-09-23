import argparse
import hashlib
import json
import math
from datetime import datetime


class Rand:
    def __init__(self, seed, year, yday, offset=0):
        m = self.md5(seed)
        s = "{}{}{}".format(m, year, yday + offset)
        self.hashstring = self.md5(s)

    @staticmethod
    def md5(s):
        return hashlib.md5(s.encode("ascii")).hexdigest()

    def getval(self):
        v = int(self.hashstring[:8], 16)
        self.hashstring = self.md5(self.hashstring[7:])
        return v


def dga(date, nr):
    with open("words.json", "r") as r:
        wt = json.load(r)

    seed = "3138C81ED54AD5F8E905555A6623C9C9"
    daydelta = 10
    year = date.year % 100
    yday = date.timetuple().tm_yday - 1

    for dayoffset in range(daydelta + 1):
        r = Rand(seed, year, yday - dayoffset)
        for _ in range(math.ceil(nr / (daydelta + 1))):
            domain = ""
            for s in ["firstword", "separator", "secondword", "tld"]:
                ss = wt[s]
                domain += ss[r.getval() % len(ss)]
            print(domain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="as YYYY-mm-dd")
    parser.add_argument("-n", "--nr", type=int, help="nr of domains to generate")
    args = parser.parse_args()
    date_str = args.date
    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date = datetime.now()
    dga(date, args.nr)
