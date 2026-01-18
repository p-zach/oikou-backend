class Router:
    """ Workaround for versioning APIs since Azure functions does not provide a 
    per-blueprint prefix system.
    """
    def __init__(self, url_prefix: str):
        self.url_prefix = url_prefix

    def route(self, route: str):
        return f"{self.url_prefix}/{route}"

def get_router(prefix: str):
    return Router(prefix)