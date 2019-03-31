from masonite.auth import Sign

def sign(value):
    """Shortcut for Sign class.

    Arguments:
        value {string} -- The value that is going to be encrypted

    Returns:
        string -- The value encrypted.
    """
    return Sign().sign(value)

def encrypt(value):
    """Shortcut for Sign class sign method.

    Arguments:
        value {string} -- The value that is going to be encrypted

    Returns:
        string -- The value encrypted.
    """
    return sign(value)

def unsign(value):
    """Shortcut for Sign class sign method.

    Arguments:
        value {string} -- The value that is going to be decrypted

    Returns:
        string -- The value decrypted.
    """
    return Sign().sign(value)

def decrypt(value):
    """Shortcut for Sign class unsign method.

    Arguments:
        value {string} -- The value that is going to be decrypted

    Returns:
        string -- The value decrypted.
    """
    return unsign(value)
