import tkinter as tk
from tkinter import messagebox
from src.tree import SearchTrie
from src.page import Page

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meu Buscador Web")
        self.trie = SearchTrie() # Instancia sua árvore de indexação

        self._create_widgets()
        self._load_sample_data() # Carrega dados de exemplo para demonstração

    def _create_widgets(self):
        # Frame para Cadastro de Páginas
        cadastro_frame = tk.LabelFrame(self.root, text="Cadastrar Página")
        cadastro_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(cadastro_frame, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = tk.Entry(cadastro_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(cadastro_frame, text="Título:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = tk.Entry(cadastro_frame, width=50)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(cadastro_frame, text="Conteúdo (Keywords p/ Indexar):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.content_text = tk.Text(cadastro_frame, width=40, height=5)
        self.content_text.grid(row=2, column=1, padx=5, pady=5)

        cadastrar_btn = tk.Button(cadastro_frame, text="Cadastrar e Indexar", command=self._add_page)
        cadastrar_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para Busca
        busca_frame = tk.LabelFrame(self.root, text="Buscar Conteúdo")
        busca_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(busca_frame, text="Termo de Busca:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = tk.Entry(busca_frame, width=50)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        buscar_btn = tk.Button(busca_frame, text="Buscar", command=self._perform_search)
        buscar_btn.grid(row=1, column=0, columnspan=2, pady=10)

        self.results_label = tk.Label(busca_frame, text="Resultados da Busca:")
        self.results_label.grid(row=2, column=0, columnspan=2, sticky="w")
        self.results_listbox = tk.Listbox(busca_frame, width=70, height=10)
        self.results_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.results_listbox.bind("<Double-Button-1>", self._open_result_url)


        # Opcional: Botão para Visualizar a Árvore (para fins de demonstração)
        # Isto exigirá uma lógica de visualização na sua classe Tree.
        view_tree_btn = tk.Button(self.root, text="Visualizar Árvore (Console)", command=self._view_tree_structure)
        view_tree_btn.pack(pady=5)


    def _add_page(self):
        url = self.url_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()

        if not url or not title or not content:
            messagebox.showwarning("Entrada Inválida", "Todos os campos devem ser preenchidos.")
            return

        new_page = Page(url, title, content)
        # Simples tokenização para pegar as palavras-chave do conteúdo
        keywords = [word.lower() for word in content.split() if len(word) > 2] # Ignora palavras pequenas

        for keyword in keywords:
            self.trie.insert(keyword, new_page) # Insere cada palavra-chave na Trie

        messagebox.showinfo("Sucesso", f"Página '{title}' indexada com sucesso!")
        self.url_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)


    def _perform_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Entrada Inválida", "Por favor, digite um termo de busca.")
            return

        self.results_listbox.delete(0, tk.END)

        # Dividir a consulta em múltiplas palavras, se houver
        query_words = [word.lower() for word in query.split()]

        # Armazenar todas as URLs encontradas para cada palavra
        all_found_urls = []
        for word in query_words:
            found_urls_for_word = self.trie.search(word)
            all_found_urls.extend(found_urls_for_word)

        # Usar um set para garantir URLs únicas e depois converter para lista
        unique_urls = list(set(all_found_urls))

        if not unique_urls:
            self.results_listbox.insert(tk.END, "Nenhum resultado encontrado.")
            return

        # Para exibir um título amigável, você precisaria de um mapeamento URL -> Página
        # Por enquanto, vamos simular que temos acesso ao objeto Page
        # Em um sistema real, você buscaria os detalhes da página por URL em outro lugar

        # Simulação: Dicionário para mapear URLs para objetos Page para exibição
        # Em um sistema real, isso seria um banco de dados ou outra estrutura
        self.indexed_pages_by_url = {}
        for page in self._sample_pages: # Usando as páginas de exemplo para popular o mapeamento
            self.indexed_pages_by_url[page.url] = page

        for url in unique_urls:
            # Tente encontrar o objeto Page correspondente para exibir o título
            page_obj = next((p for p in self._sample_pages if p.url == url), None) # Gambiarra para pegar o objeto Page
            if page_obj:
                self.results_listbox.insert(tk.END, f"{page_obj.title} ({page_obj.url})")
            else:
                self.results_listbox.insert(tk.END, url) # Caso não encontre o objeto Page

    def _load_sample_data(self):
        # Carrega dados de exemplo para não começar do zero na demo
        self._sample_pages = [
            Page("https://example.com/pagina1", "Python é Incrível", "Python é uma linguagem de programação incrível para desenvolvimento web e análise de dados."),
            Page("https://example.com/pagina2", "Estruturas de Dados Essenciais", "Aprender árvores e grafos é fundamental em estruturas de dados."),
            Page("https://example.com/pagina3", "Desenvolvimento Web com Python", "Construindo aplicações web robustas com frameworks Python."),
            Page("https://example.com/pagina4", "Algoritmos e Análise", "Estudando algoritmos e sua complexidade para otimizar soluções."),
        ]
        for page in self._sample_pages:
            keywords = [word.lower() for word in page.content.split() if len(word) > 2]
            for keyword in keywords:
                self.trie.insert(keyword, page)
        messagebox.showinfo("Dados Carregados", "Dados de exemplo carregados para demonstração.")

    def _open_result_url(self, event):
        # Função para abrir a URL quando o item é clicado na Listbox
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_text = self.results_listbox.get(selected_index[0])
            # Extrair a URL do texto exibido (entre parênteses)
            import re
            match = re.search(r'\((.*?)\)', selected_text)
            if match:
                url = match.group(1)
                import webbrowser
                webbrowser.open_new(url)
            else:
                messagebox.showerror("Erro", "Não foi possível extrair a URL.")


    def _view_tree_structure(self):
        # Este método vai chamar uma função na sua classe Tree para imprimir
        # a estrutura da árvore no console ou em uma nova janela.
        # Implementação real dependerá da sua classe Tree.
        print("\n--- Estrutura da Árvore (Exemplo de In-Order Traversal para BST/AVL) ---")
        # Exemplo: se sua Trie tivesse um método para printar:
        # self.trie.print_tree_structure()
        # Para Trie, você pode fazer uma BFS ou DFS para printar os nós e suas páginas
        q = [(self.trie.root, "")]
        while q:
            node, path = q.pop(0)
            print(f"Node: '{path}' (End of Word: {node.is_end_of_word}, Pages: {[p for p in node.pages]})")
            for char, child in node.children.items():
                q.append((child, path + char))
        print("--------------------------------------------------\n")
        messagebox.showinfo("Visualização da Árvore", "Estrutura da árvore impressa no console.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()