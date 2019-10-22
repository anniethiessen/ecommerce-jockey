class ApiInvalidToken(Exception):
    def __init__(self):
        Exception.__init__(self, "Invalid token")


class ApiInvalidContentToken(Exception):
    def __init__(self):
        Exception.__init__(self, "Invalid content token")


class ApiRateLimitExceeded(Exception):
    def __init__(self):
        Exception.__init__(self, "Rate limit exceeded")
