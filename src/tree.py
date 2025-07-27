# src/tree.py
from src.node import TrieNode # assuming TrieNode is correctly defined here or imported into this file
from src.page import Page

class TrieNode: # Se TrieNode estiver neste arquivo, garanta que seja assim
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False # ESSENCIAL: Adicione esta linha se não tiver!
        self.pages = set() # Deve ser um set de objetos Page

    def add_page(self, page_obj: Page):
        self.pages.add(page_obj)

    def get_pages(self) -> list[Page]:
        return list(self.pages)

class SearchTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, page: Page):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True # ESSENCIAL: Mantem esta propriedade
        node.add_page(page) # CORREÇÃO CRÍTICA: Passa o objeto Page completo

    def search(self, word: str) -> list[Page]:
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        found_pages = set()
        self._collect_pages(node, found_pages)
        return list(found_pages)

    def _collect_pages(self, node: TrieNode, page_set: set):
        if node.pages:
            page_set.update(node.pages)

        for char_key in node.children:
            self._collect_pages(node.children[char_key], page_set)

    # ... (outros métodos como starts_with, delete, se você os adicionou)