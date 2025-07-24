class Page:
    def __init__(self, url: str, title: str, content: str, keywords: list = None):
        self.url = url
        self.title = title
        self.content = content # Ou um caminho para o arquivo de conteúdo
        self.keywords = keywords if keywords is not None else []
        # Opcional: self.last_indexed_date, self.size, etc.

    def __repr__(self):
        return f"Page(title='{self.title}', url='{self.url}')"

    def add_keyword(self, keyword: str):
        if keyword not in self.keywords:
            self.keywords.append(keyword)

    def get_keywords(self):
        # Processar o conteúdo para extrair palavras-chave ou usar as pré-definidas
        if not self.keywords and self.content:
            # Exemplo simples: dividir o conteúdo em palavras
            # Em um buscador real, você faria tokenização, remoção de stopwords, stemming etc.
            self.keywords = [word.lower() for word in self.content.split() if len(word) > 2]
        return self.keywords