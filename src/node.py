class TrieNode:
    def __init__(self):
        self.children = {}  # Dicionário para mapear caracteres a nós filhos
        self.is_end_of_word = False # Indica se este nó marca o fim de uma palavra
        self.pages = set() # Conjunto de objetos Page ou IDs de páginas associadas a esta palavra

    def add_page(self, page_id): # page_id pode ser a URL ou um ID único
        self.pages.add(page_id)

    def get_pages(self):
        return list(self.pages)