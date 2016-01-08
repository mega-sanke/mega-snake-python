def decode(msg):
    exec ('x = ' + msg)
    return x


def encode(msg):
    return str(msg)
