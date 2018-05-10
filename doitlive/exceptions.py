class DoItLiveError(Exception):
    """Base exception class for all doitlive-related errors."""
    pass


class ConfigurationError(DoItLiveError):
    pass


class SessionError(DoItLiveError):
    pass
