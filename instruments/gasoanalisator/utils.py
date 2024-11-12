def get_i_bit(a, i):
    return (a >> (7 - i)) & 1


def get_combined_data(data):
    combined_data = []

    for i in range(0, len(data), 2):
        combined_data.append((data[i + 1] << 4) | data[i])

    return combined_data[::-1]


def float_from_bytes(data):
    combined_data = get_combined_data(data)

    a = combined_data[0]
    num_sign = get_i_bit(a, 0)
    power_sign = get_i_bit(a, 1)
    power = a & 0b111111
    mantis = (combined_data[1] << 8) | combined_data[2]

    if power_sign:
        power = 0b111111 - power + 1

    if num_sign:
        mantis = 0b1111111111111111 - mantis + 1

    return ((-1) ** num_sign) * (2 ** (power * (-1) ** power_sign)) * (mantis / 2**16)


def checksum(a):
    chksum = 0
    for el in a:
        chksum ^= el
    return checksum
