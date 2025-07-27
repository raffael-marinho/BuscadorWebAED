# src/page.py
class Page:
    def __init__(self, url, title, content):
        self.url = url
        self.title = title
        self.content = content

    def __repr__(self):
        return f"Page(title='{self.title}', url='{self.url}')"

    def __eq__(self, other):
        if not isinstance(other, Page):
            return NotImplemented
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)