""" Masonite Exceptions """

class DriverNotFound(Exception):
    """ Thrown when drivers are not found """
    pass


class DriverLibraryNotFound(Exception):
    """ Thrown when driver libraries are not found """
    pass


class FileTypeException(Exception):
    """ Thrown when file types are incorrect """
    pass


class RequiredContainerBindingNotFound(Exception):
    pass


class MissingContainerBindingNotFound(Exception):
    pass


class UnacceptableDriverType(Exception):
    pass


class ContainerError(Exception):
    pass


class InvalidCSRFToken(Exception):
    """ Thrown when CSRF tokens expire or are incorrect are not found """
    pass


class InvalidHTTPStatusCode(Exception):
    """ Thrown when there is an invalid http status code """
    pass


class RouteMiddlewareNotFound(Exception):
    """ Thrown when route middleware is not found """
    pass


class ResponseError(Exception):
    pass


class InvalidAutoloadPath(Exception):
    pass


class AutoloadContainerOverwrite(Exception):
    pass


class InvalidSecretKey(Exception):
    pass


class StrictContainerException(Exception):
    pass


class InvalidRouteCompileException(Exception):
    pass


class RouteException(Exception):
    pass
