from src.node import TrieNode
from src.page import Page

class SearchTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, page: Page):
        node = self.root
        for char in word.lower(): # Armazena palavras em minúsculas
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.add_page(page.url) # Adiciona a URL da página ao conjunto de páginas do nó

    def search(self, word: str) -> list:
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return [] # Palavra não encontrada
            node = node.children[char]
        return node.get_pages() # Retorna as URLs das páginas associadas

    def starts_with(self, prefix: str) -> list:
        # Opcional: para funcionalidade de autocompletar
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Percorrer a subárvore para encontrar todas as palavras e suas páginas
        results = []
        stack = [(node, prefix.lower())]
        while stack:
            current_node, current_word = stack.pop()
            if current_node.is_end_of_word:
                results.extend(current_node.get_pages())
            for char, child_node in current_node.children.items():
                stack.append((child_node, current_word + char))
        return list(set(results)) # Retorna URLs únicas

    def delete(self, word: str, page_url: str = None):
        # Implementação de remoção é mais complexa em uma Trie
        # Você precisaria remover a página de `node.pages` e,
        # se o nó não for mais fim de palavra e não tiver filhos,
        # remover o nó da árvore (recursivamente).
        # Para o MVP, pode-se focar em remover apenas a referência à página.
        pass # Implementar depois