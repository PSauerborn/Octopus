"""Module containing request functions used to make traced requests.
All requests are made over the Python requests library; if tracing
has been enabled in the Environment Variables, then the call is 
traced. If not, the Python requests function is evaluated as normal"""

import requests

from Octopus.bottle.jaeger import tracing


def post(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make POST request. Requests
    are made by providing the tracing.traced_request()
    function with the POST function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """

    return tracing.traced_request(requests.post, url, *args, **kwargs)

def get(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make GET request. Requests
    are made by providing the tracing.traced_request()
    function with the GET function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """

    return tracing.traced_request(requests.get, url, *args, **kwargs)

def patch(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make PATCH request. Requests
    are made by providing the tracing.traced_request()
    function with the PATCH function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """

    return tracing.traced_request(requests.patch, url, *args, **kwargs)

def delete(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make DELETE request. Requests
    are made by providing the tracing.traced_request()
    function with the DELETE function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """

    return tracing.traced_request(requests.delete, url, *args, **kwargs)

def head(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make HEAD request. Requests
    are made by providing the tracing.traced_request()
    function with the HEAD function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """
    return tracing.traced_request(requests.head, url, *args, **kwargs)

def put(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make PUT request. Requests
    are made by providing the tracing.traced_request()
    function with the PUT function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """
    return tracing.traced_request(requests.put, url, *args, **kwargs)

def options(url: str, *args: tuple, **kwargs: dict) -> object:
    """Function used to make OPTIONS request. Requests
    are made by providing the tracing.traced_request()
    function with the OPTIONS function from the requests 
    library
    
    Arguments:
        url: str giving url

    Returns:
        response object from request
    """
    return tracing.traced_request(requests.options, url, *args, **kwargs)