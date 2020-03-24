class BaseError(Exception):
    """Base connector error."""


class NodeError(BaseError):
    """Node returns an error."""


class NodeInvalidResponceError(NodeError):
    """Node returns a invalid response."""


class NetworkError(BaseError):
    """Node network error."""


class NetworkTimeoutError(NetworkError):
    """Node request riches timeout."""


# warnings


class BaseWarning(Warning):
    """Base connector warning."""
