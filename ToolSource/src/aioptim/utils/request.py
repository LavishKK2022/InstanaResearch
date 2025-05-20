"""
Connection utility class, offering a reusable set of methods
to perform internet-facing requests.

For consistency, classes should extend the Conn class, to make
use of its functionality.
"""
from requests import get, post


class Conn:
    """Conn offers a streamlined way of processing requests."""

    def get_req(self, endpoint, headers, params):
        """
        Performs a GET request to the specified endpoint.

        Args:
            endpoint: URL endpoint to retrieve information from
            headers: dictionary containing data to be passed as headers
            params: parameters to be included in the URL (?:)

        Raises:
            ConnectionError: endpoint cannot be reached

        Returns:
            The response of performing the GET request

        """
        try:
            return get(
                url=Conn._construct_path(self.url, endpoint),
                headers=headers,
                params=params
            ).json()
        except Exception:
            raise ConnectionError(f"{self.url} not reached, check connection")

    def post_req(self, endpoint, data, params, headers):
        """
        Performs a POST request to the specified endpoint.

        Args:
            endpoint: URL endpoint to send information to
            data: data to send as part of the POST request
            params: parameters to be included in the URL (?:)
            headers: dictionary containing data to be passed as headers

        Raises:
            ConnectionError: endpoint cannot be reached

        Returns:
            The response of performing the POST request
        """
        try:
            return post(
                url=Conn._construct_path(self.url, endpoint),
                json=data,
                headers=headers,
                params=params
            ).json()
        except Exception:
            raise ConnectionError(f"{self.url} not reached, check connection")

    @staticmethod
    def _construct_path(*args):
        """
        Constructs URL based on the arguments

        Returns:
            Joined string forming the complete URL
        """
        return "".join(args)
