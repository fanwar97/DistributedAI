import argparse


def ror32(v, n):
    return ((v >> n) | (v << (32 - n))) & 0xFFFFFFFF


def next_domain(r, c, l, tld):
    domain = ""
    for _ in range(l):
        r = ror32((321167 * r + c) & 0xFFFFFFFF, 16)
        domain += chr((r & 0x17FF) % 26 + ord("a"))

    domain += tld
    print(domain)
    return r


def dga(version, nr):
    if version == 1:
        r = 0xC87C8A78
        c = -1719405398
        l = 17
        tld = ".net"
    elif version == 2:
        r = 0x851A3E59
        c = -1916503263
        l = 10
        tld = ".com"
    for _ in range(nr):
        r = next_domain(r, c, l, tld)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DGA of Fobber")
    parser.add_argument("version", choices=[1, 2], type=int)
    parser.add_argument("-n", "--nr", type=int, help="nr of domains to generate")
    args = parser.parse_args()
    dga(args.version, args.nr)
