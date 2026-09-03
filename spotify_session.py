class SpotifySession:
    def __init__(self, page):
        self.page = page
        self.api_headers: dict | None = None
        self.saved_uri: str | None = None

    def __repr__(self):
        return f'''
{self.page=}
{self.api_headers=}
{self.saved_uri=}'''