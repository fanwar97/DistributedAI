def int_to_ubyte(num):
    return num.to_bytes(1, "big", signed = False)
def int_to_Nubyte(num, N):
    return num.to_bytes(N, "big", signed = False)