""" Masonite Exceptions """

class DriverNotFound(Exception):
    """ Thrown when the driver can not be found """
    pass


class DriverLibraryNotFound(Exception):
    """ Thrown when driver libraries are not found """
    pass


class FileTypeException(Exception):
    """ Thrown when file types are incorrect """
    pass


class RequiredContainerBindingNotFound(Exception):
    """ Thrown when the Cache key binding is not found in the container """
    pass


class MissingContainerBindingNotFound(Exception):
    """ Thrown if the key is not in the container """
    pass


class UnacceptableDriverType(Exception):
    """ Thrown when a driver passed in is not a string or a class """
    pass


class ContainerError(Exception):
    """ Thrown when the container is not loaded into the class """
    pass


class InvalidCSRFToken(Exception):
    """ Thrown when CSRF tokens are invalid """
    pass


class InvalidHTTPStatusCode(Exception):
    """ Thrown when there is an invalid http status code """
    pass


class RouteMiddlewareNotFound(Exception):
    """ Thrown when route middleware is not found """
    pass


class ResponseError(Exception):
    """ Thrown when an acceptable response type was not returned"""
    pass


class InvalidAutoloadPath(Exception):
    """ Thrown when the search path ends with a forward  """
    pass


class AutoloadContainerOverwrite(Exception):
    """ Thrown when the container already has the key binding """
    pass


class InvalidSecretKey(Exception):
    """ Thrown if the secret key does not exist """
    pass


class StrictContainerException(Exception):
    """ Thrown when tryingto override a key inside a strict container """
    pass


class InvalidRouteCompileException(Exception):
    """ Thrown when a user's route compiler is not an available route compiler """
    pass


class RouteException(Exception):
    """ Thrown when method type needs to be a list  """
    pass
