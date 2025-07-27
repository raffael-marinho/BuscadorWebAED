import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import re
import requests
from bs4 import BeautifulSoup
from collections import deque

# --- Importações das suas classes personalizadas ---
# Certifique-se de que Page está em 'src/page.py' e TrieNode/SearchTrie em 'src/tree.py'.
# As definições completas dessas classes NÃO DEVEM estar aqui, apenas a importação.
from src.page import Page
from src.tree import TrieNode, SearchTrie

# --- Estilo e Configurações Globais ---
PRIMARY_COLOR = '#007ACC'
SECONDARY_COLOR = '#FFFFFF'
ACCENT_COLOR = '#4CAF50'
BACKGROUND_COLOR = '#F5F7FA'
CARD_BG_COLOR = '#FFFFFF'
BORDER_COLOR = '#E0E0E0'
TEXT_COLOR = '#333333'
LIGHT_TEXT_COLOR = '#666666'
PLACEHOLDER_COLOR = '#A0A0A0'
HOVER_COLOR = '#005F99'

FONT_FALLBACK = ['Segoe UI', 'Helvetica Neue', 'Roboto', 'Arial', 'sans-serif']

FONT_SIZE_SMALL = 10
FONT_SIZE_MEDIUM = 12
FONT_SIZE_LARGE = 15
FONT_SIZE_XL = 20
FONT_SIZE_TITLE = 24

CARD_RADIUS = 10
SHADOW_OFFSET = 5
SHADOW_COLOR = '#CCCCCC'

class SearchApp:
    def __init__(self, root):
        self.root = root
        # Título da janela sem emoji
        self.root.title("Buscador Web IFPE") 
        self.root.geometry("1300x720")
        self.root.minsize(1200, 650)
        self.root.configure(bg=BACKGROUND_COLOR)
        
        self.root.update_idletasks()
        center_x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        center_y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{center_x}+{center_y}')

        self._configure_grid()

        self.trie = SearchTrie()
        self.visited_urls = set()
        self._create_styles()
        self._create_widgets()
        self._load_sample_data()
        self._setup_placeholders()

    def _configure_grid(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(1, weight=1)

    def _create_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure('.',
                        background=BACKGROUND_COLOR,
                        foreground=TEXT_COLOR,
                        font=(FONT_FALLBACK, FONT_SIZE_MEDIUM))

        style.configure('Header.TFrame', background=PRIMARY_COLOR)
        # Título do cabeçalho sem emoji
        style.configure('Header.TLabel',
                        font=(FONT_FALLBACK, FONT_SIZE_TITLE, 'bold'),
                        background=PRIMARY_COLOR,
                        foreground=SECONDARY_COLOR,
                        padding=(20, 15))

        style.configure('Card.TFrame',
                        background=CARD_BG_COLOR,
                        relief='flat',
                        borderwidth=0)
        style.configure('CardHeader.TLabel',
                        background=CARD_BG_COLOR,
                        font=(FONT_FALLBACK, FONT_SIZE_LARGE, 'bold'),
                        foreground=PRIMARY_COLOR,
                        padding=(15, 15))

        style.configure('TEntry',
                        font=(FONT_FALLBACK, FONT_SIZE_MEDIUM),
                        padding=10,
                        fieldbackground=SECONDARY_COLOR,
                        foreground=TEXT_COLOR,
                        borderwidth=1,
                        relief='solid',
                        bordercolor=BORDER_COLOR)

        style.configure('TButton',
                        font=(FONT_FALLBACK, FONT_SIZE_MEDIUM, 'bold'),
                        padding=12,
                        background=PRIMARY_COLOR,
                        foreground=SECONDARY_COLOR,
                        borderwidth=0,
                        relief='flat',
                        focusthickness=0)
        style.map('TButton',
                  background=[('active', HOVER_COLOR), ('!disabled', PRIMARY_COLOR)],
                  foreground=[('active', SECONDARY_COLOR)])

        style.configure('Hover.TButton',
                        background=HOVER_COLOR,
                        foreground=SECONDARY_COLOR)

        self.root.option_add('*Listbox.font', (FONT_FALLBACK, FONT_SIZE_MEDIUM))
        self.root.option_add('*Listbox.background', SECONDARY_COLOR)
        self.root.option_add('*Listbox.foreground', TEXT_COLOR)
        self.root.option_add('*Listbox.selectBackground', PRIMARY_COLOR)
        self.root.option_add('*Listbox.selectForeground', SECONDARY_COLOR)
        self.root.option_add('*Listbox.borderwidth', 0)
        self.root.option_add('*Listbox.relief', 'flat')
        self.root.option_add('*Listbox.highlightthickness', 0)

        style.configure('TScrollbar',
                        troughcolor=CARD_BG_COLOR,
                        background=BORDER_COLOR,
                        borderwidth=0,
                        relief='flat')
        style.map('TScrollbar',
                  background=[('active', PRIMARY_COLOR)])

        style.configure('TLabel',
                        background=CARD_BG_COLOR,
                        foreground=TEXT_COLOR,
                        font=(FONT_FALLBACK, FONT_SIZE_MEDIUM))
        style.configure('Small.TLabel',
                        font=(FONT_FALLBACK, FONT_SIZE_SMALL, 'bold'),
                        background=CARD_BG_COLOR,
                        foreground=LIGHT_TEXT_COLOR)
        
        style.configure('TProgressbar',
                        background=ACCENT_COLOR,
                        troughcolor=BORDER_COLOR,
                        thickness=20)

    def _create_shadow_card(self, parent, initial_width, initial_height, row, column, padx, pady, columnspan=1, rowspan=1, sticky='nsew'):
        canvas = tk.Canvas(parent,
                            bg=BACKGROUND_COLOR,
                            highlightthickness=0,
                            relief='flat',
                            width=initial_width, height=initial_height)
        
        canvas.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky, columnspan=columnspan, rowspan=rowspan)

        shadow_rect_id = canvas.create_rounded_rectangle(
            SHADOW_OFFSET, SHADOW_OFFSET,
            initial_width - 1, initial_height - 1,
            radius=CARD_RADIUS,
            fill=SHADOW_COLOR,
            outline=SHADOW_COLOR,
            tags="shadow_rect"
        )
        
        card_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        card_rect_id = canvas.create_rounded_rectangle(
            1, 1,
            initial_width - 1 - SHADOW_OFFSET, initial_height - 1 - SHADOW_OFFSET,
            radius=CARD_RADIUS,
            fill=CARD_BG_COLOR,
            outline=BORDER_COLOR,
            width=1,
            tags="card_rect"
        )
        
        # Aqui, estamos criando a janela interna no canvas.
        # Definimos seu tamanho inicial para que se ajuste à área do card.
        card_window_id = canvas.create_window(
            (initial_width - SHADOW_OFFSET) / 2, # x central
            (initial_height - SHADOW_OFFSET) / 2, # y central
            window=card_frame,
            width=initial_width - (SHADOW_OFFSET * 2) - 2, # Largura ajustada
            height=initial_height - (SHADOW_OFFSET * 2) - 2, # Altura ajustada
            tags="card_window"
        )
        
        # Propaga o redimensionamento do frame pai (container) para o canvas,
        # e o canvas para as formas e o frame interno.
        canvas.bind('<Configure>', lambda e: self._on_canvas_resize(canvas, card_frame))

        return card_frame, canvas

    def _on_canvas_resize(self, canvas, card_frame):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Atualiza a sombra
        canvas.coords("shadow_rect",
                      SHADOW_OFFSET, SHADOW_OFFSET,
                      canvas_width - 1, canvas_height - 1)
        
        # Atualiza o retângulo principal do card
        canvas.coords("card_rect",
                      1, 1,
                      canvas_width - SHADOW_OFFSET - 1, canvas_height - SHADOW_OFFSET - 1)
        
        # Calcula a nova largura e altura para o card_frame
        card_frame_new_width = canvas_width - (SHADOW_OFFSET * 2) - 2
        card_frame_new_height = canvas_height - (SHADOW_OFFSET * 2) - 2

        # Verifica se as dimensões são válidas antes de aplicar
        if card_frame_new_width > 0 and card_frame_new_height > 0:
            # Reposiciona o item 'window' no canvas para o centro
            canvas.coords("card_window",
                          (canvas_width - SHADOW_OFFSET) / 2,
                          (canvas_height - SHADOW_OFFSET) / 2)
            
            # Redimensiona o widget 'card_frame' real dentro do 'window' do canvas
            card_frame.configure(width=card_frame_new_width, height=card_frame_new_height)
        else:
            # Garante que as dimensões não sejam negativas
            card_frame.configure(width=1, height=1)


    def _inject_rounded_rectangle_method(self):
        if not hasattr(tk.Canvas, 'create_rounded_rectangle'):
            def _round_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
                points = [x1+radius, y1,
                          x2-radius, y1,
                          x2, y1,
                          x2, y1+radius,
                          x2, y2-radius,
                          x2, y2,
                          x2-radius, y2,
                          x1+radius, y2,
                          x1, y2,
                          x1, y2-radius,
                          x1, y1+radius,
                          x1, y1]
                return self.create_polygon(points, smooth=True, **kwargs)
            
            tk.Canvas.create_rounded_rectangle = _round_rect


    def _create_widgets(self):
        self._inject_rounded_rectangle_method()

        header = ttk.Frame(self.root, style='Header.TFrame')
        header.grid(row=0, column=0, columnspan=3, sticky='nsew')
        header.columnconfigure(0, weight=1)
        
        ttk.Label(header, text='Buscador Web IFPE', style='Header.TLabel', anchor='center').pack(expand=True, fill='both')

        container = ttk.Frame(self.root, padding=(20, 20, 20, 10)) 
        container.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=20, pady=20)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=1)
        container.rowconfigure(0, weight=1)

        self.cadastro_card_frame, _ = self._create_shadow_card(
            container, 400, 580,
            row=0, column=0, sticky='nsew', padx=(0,15), pady=(0,20)
        )
        self._build_cadastro_card_content(self.cadastro_card_frame)

        self.busca_card_frame, self.busca_card_canvas = self._create_shadow_card(
            container, 450, 580,
            row=0, column=1, sticky='nsew', padx=(15,15), pady=(0,20)
        )
        self._build_busca_card_content(self.busca_card_frame)

        self.crawler_card_frame, _ = self._create_shadow_card(
            container, 400, 580,
            row=0, column=2, sticky='nsew', padx=(15,0), pady=(0,20)
        )
        self._build_crawler_card_content(self.crawler_card_frame)

        # Botão visualizar árvore sem emoji
        view_btn = ttk.Button(self.root, text='Ver Estrutura da Arvore (Console)', command=self._view_tree_structure)
        view_btn.grid(row=2, column=0, columnspan=3, pady=(0,20))
        self._add_hover_effect(view_btn)

    def _build_cadastro_card_content(self, card_frame):
        card_frame.columnconfigure(0, weight=1)

        # Título do card sem emoji
        ttk.Label(card_frame, text='Cadastrar Nova Pagina', style='CardHeader.TLabel').grid(row=0, column=0, sticky='ew', pady=(0,10), padx=15)
        
        ttk.Label(card_frame, text='URL:', style='Small.TLabel').grid(row=1, column=0, sticky='w', padx=15, pady=2)
        self.url_entry = ttk.Entry(card_frame, style='TEntry')
        self.url_entry.grid(row=2, column=0, sticky='ew', padx=15, pady=5)

        ttk.Label(card_frame, text='Titulo:', style='Small.TLabel').grid(row=3, column=0, sticky='w', padx=15, pady=2)
        self.title_entry = ttk.Entry(card_frame, style='TEntry')
        self.title_entry.grid(row=4, column=0, sticky='ew', padx=15, pady=5)

        ttk.Label(card_frame, text='Palavras-chave (separadas por virgula):', style='Small.TLabel').grid(row=5, column=0, sticky='nw', padx=15, pady=2)
        self.content_text = tk.Text(card_frame, height=8, font=(FONT_FALLBACK, FONT_SIZE_MEDIUM),
                                         wrap='word', bd=1, relief='solid', highlightthickness=0,
                                         bg=SECONDARY_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.content_text.grid(row=6, column=0, sticky='ew', padx=15, pady=5)
        
        add_btn = ttk.Button(card_frame, text='Adicionar e Indexar', command=self._add_page)
        add_btn.grid(row=7, column=0, pady=20)
        self._add_hover_effect(add_btn)

        card_frame.grid_rowconfigure(6, weight=1)


    def _build_busca_card_content(self, card_frame):
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(2, weight=1)

        # Título do card sem emoji
        ttk.Label(card_frame, text='Buscar Conteudo', style='CardHeader.TLabel').grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,10), padx=15)
        
        search_input_frame = ttk.Frame(card_frame, style='Card.TFrame') 
        search_input_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=15, pady=(0,10))
        search_input_frame.columnconfigure(0, weight=1)
        
        self.search_entry = ttk.Entry(search_input_frame, style='TEntry')
        self.search_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5)) 
        search_btn = ttk.Button(search_input_frame, text='Buscar', command=self._perform_search)
        search_btn.grid(row=0, column=1, padx=(5, 0)) 
        self._add_hover_effect(search_btn)

        result_container_frame = ttk.Frame(card_frame, style='Card.TFrame', relief='solid', borderwidth=1) 
        result_container_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=15, pady=(5,15))
        result_container_frame.rowconfigure(0, weight=1)
        result_container_frame.columnconfigure(0, weight=1)

        self.results_listbox = tk.Listbox(result_container_frame, selectmode=tk.SINGLE)
        sb = ttk.Scrollbar(result_container_frame, orient='vertical', command=self.results_listbox.yview, style='TScrollbar')
        self.results_listbox.config(yscrollcommand=sb.set)
        
        self.results_listbox.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        sb.grid(row=0, column=1, sticky='ns')
        
        self.results_listbox.bind('<Double-Button-1>', self._open_result_url)

    def _build_crawler_card_content(self, card_frame):
        card_frame.columnconfigure(0, weight=1)

        ttk.Label(card_frame, text='Automacao (Crawler)', style='CardHeader.TLabel').grid(row=0, column=0, sticky='ew', pady=(0,10), padx=15)

        ttk.Label(card_frame, text='URL de Inicio:', style='Small.TLabel').grid(row=1, column=0, sticky='w', padx=15, pady=2)
        self.crawler_url_entry = ttk.Entry(card_frame, style='TEntry')
        self.crawler_url_entry.grid(row=2, column=0, sticky='ew', padx=15, pady=5)

        ttk.Label(card_frame, text='Profundidade de Crawling (0 para apenas a pagina inicial):', style='Small.TLabel').grid(row=3, column=0, sticky='w', padx=15, pady=2)
        self.crawler_depth_entry = ttk.Entry(card_frame, style='TEntry')
        self.crawler_depth_entry.grid(row=4, column=0, sticky='ew', padx=15, pady=5)
        self.crawler_depth_entry.insert(0, '1')

        start_crawl_btn = ttk.Button(card_frame, text='Iniciar Crawling', command=self._start_crawling)
        start_crawl_btn.grid(row=5, column=0, pady=20)
        self._add_hover_effect(start_crawl_btn)

        ttk.Label(card_frame, text='Status do Crawler:', style='Small.TLabel').grid(row=6, column=0, sticky='w', padx=15, pady=5)
        self.crawler_log_text = tk.Text(card_frame, height=10, font=(FONT_FALLBACK, FONT_SIZE_SMALL),
                                             wrap='word', bd=1, relief='solid', highlightthickness=0,
                                             bg=SECONDARY_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                             state='disabled')
        self.crawler_log_text.grid(row=7, column=0, sticky='nsew', padx=15, pady=5)
        
        self.crawler_progress_bar = ttk.Progressbar(card_frame, orient='horizontal', mode='determinate', style='TProgressbar')
        self.crawler_progress_bar.grid(row=8, column=0, sticky='ew', padx=15, pady=(10, 5))
        self.crawler_progress_label = ttk.Label(card_frame, text='0% Concluido', style='Small.TLabel')
        self.crawler_progress_label.grid(row=9, column=0, sticky='ew', padx=15)

        card_frame.grid_rowconfigure(7, weight=1)


    def _add_hover_effect(self, widget):
        def on_enter(e):
            widget.config(style='Hover.TButton')
        def on_leave(e):
            widget.config(style='TButton')

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _setup_placeholders(self):
        self.url_entry.insert(0, 'Ex: https://ifpe.edu.br/projeto')
        self.url_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(self.url_entry, 'Ex: https://ifpe.edu.br/projeto'))
        self.url_entry.bind('<FocusOut>', lambda e: self._set_placeholder(self.url_entry, 'Ex: https://ifpe.edu.br/projeto'))
        self.url_entry.config(foreground=PLACEHOLDER_COLOR)

        self.title_entry.insert(0, 'Ex: Meu Projeto Incrivel')
        self.title_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(self.title_entry, 'Ex: Meu Projeto Incrivel'))
        self.title_entry.bind('<FocusOut>', lambda e: self._set_placeholder(self.title_entry, 'Ex: Meu Projeto Incrivel'))
        self.title_entry.config(foreground=PLACEHOLDER_COLOR)

        self.content_text.insert('1.0', 'Ex: python, tkinter, busca, web (separadas por virgula)')
        self.content_text.bind('<FocusIn>', lambda e: self._clear_text_placeholder(self.content_text, 'Ex: python, tkinter, busca, web (separadas por virgula)'))
        self.content_text.bind('<FocusOut>', lambda e: self._set_text_placeholder(self.content_text, 'Ex: python, tkinter, busca, web (separadas por virgula)'))
        self.content_text.config(foreground=PLACEHOLDER_COLOR)

        self.search_entry.insert(0, 'Digite seu termo de busca aqui...')
        self.search_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(self.search_entry, 'Digite seu termo de busca aqui...'))
        self.search_entry.bind('<FocusOut>', lambda e: self._set_placeholder(self.search_entry, 'Digite seu termo de busca aqui...'))
        self.search_entry.config(foreground=PLACEHOLDER_COLOR)

        self.crawler_url_entry.insert(0, 'Ex: https://ifpe.edu.br')
        self.crawler_url_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(self.crawler_url_entry, 'Ex: https://ifpe.edu.br'))
        self.crawler_url_entry.bind('<FocusOut>', lambda e: self._set_placeholder(self.crawler_url_entry, 'Ex: https://ifpe.edu.br'))
        self.crawler_url_entry.config(foreground=PLACEHOLDER_COLOR)
        
        self.crawler_depth_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(self.crawler_depth_entry, '1'))
        self.crawler_depth_entry.bind('<FocusOut>', lambda e: self._set_placeholder(self.crawler_depth_entry, '1'))
        self.crawler_depth_entry.config(foreground=PLACEHOLDER_COLOR)


    def _clear_placeholder(self, entry_widget, placeholder_text):
        if entry_widget.get() == placeholder_text:
            entry_widget.delete(0, tk.END)
            entry_widget.config(foreground=TEXT_COLOR)

    def _set_placeholder(self, entry_widget, placeholder_text):
        if not entry_widget.get():
            entry_widget.insert(0, placeholder_text)
            entry_widget.config(foreground=PLACEHOLDER_COLOR)

    def _clear_text_placeholder(self, text_widget, placeholder_text):
        if text_widget.get('1.0', tk.END).strip() == placeholder_text:
            text_widget.delete('1.0', tk.END)
            text_widget.config(foreground=TEXT_COLOR)

    def _set_text_placeholder(self, text_widget, placeholder_text):
        if not text_widget.get('1.0', tk.END).strip():
            text_widget.insert('1.0', placeholder_text)
            text_widget.config(foreground=PLACEHOLDER_COLOR)

    def _add_page_to_trie(self, url, title, content):
        """Método auxiliar para adicionar uma página à Trie, seja do cadastro manual ou do crawler."""
        p = Page(url, title, content)
        words_indexed = 0
        # Divide o conteúdo por vírgulas ou espaços e pega palavras com 3+ letras
        for w in [w.lower() for w in re.findall(r'\b\w{3,}\b', re.sub(r'[,;]', ' ', content))]:
            self.trie.insert(w, p)
            words_indexed += 1
        return words_indexed

    def _add_page(self):
        url = self.url_entry.get().strip()
        title = self.title_entry.get().strip()
        keywords_text = self.content_text.get('1.0', tk.END).strip()

        if url == 'Ex: https://ifpe.edu.br/projeto': url = ''
        if title == 'Ex: Meu Projeto Incrível': title = ''
        if keywords_text == 'Ex: python, tkinter, busca, web (separadas por vírgula)': keywords_text = ''

        if not url or not title or not keywords_text:
            messagebox.showwarning('Campos Vazios', 'Por favor, preencha todos os campos para cadastrar uma pagina.')
            return
        
        if not re.match(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', url):
            messagebox.showerror('URL Invalida', 'Por favor, insira uma URL valida (ex: https://ifpe.edu.br/exemplo).')
            return

        words_indexed = self._add_page_to_trie(url, title, keywords_text)
            
        messagebox.showinfo('Sucesso', f"Pagina '{title}' foi indexada com sucesso! ({words_indexed} palavras indexadas).")
        
        self.url_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_text.delete('1.0', tk.END)
        self._set_placeholder(self.url_entry, 'Ex: https://ifpe.edu.br/projeto')
        self._set_placeholder(self.title_entry, 'Ex: Meu Projeto Incrivel')
        self._set_text_placeholder(self.content_text, 'Ex: python, tkinter, busca, web (separadas por virgula)')

    def _perform_search(self):
        query = self.search_entry.get().strip()
        
        if query == 'Digite seu termo de busca aqui...': query = ''

        self.results_listbox.delete(0, tk.END)
        if not query:
            messagebox.showwarning('Entrada Invalida', 'Por favor, digite um termo para realizar a busca.')
            return
        
        found_pages = []
        search_terms = [w.lower() for w in re.findall(r'\b\w+\b', query)]

        for term in search_terms:
            results = self.trie.search(term)
            if results:
                found_pages.extend(results)

        unique_pages = list(dict.fromkeys(found_pages)) 

        if not unique_pages:
            self.results_listbox.insert(tk.END, 'Nenhum resultado encontrado para sua busca.')
        else:
            self.results_listbox.insert(tk.END, f"Resultados para '{query}':")
            self.results_listbox.insert(tk.END, "--------------------------")
            for i, p in enumerate(unique_pages):
                self.results_listbox.insert(tk.END, f"-> {p.title} ({p.url})")
            self.results_listbox.insert(tk.END, "--------------------------")
            self.results_listbox.insert(tk.END, "Dica: Clique duas vezes para abrir o link no navegador.")


    def _open_result_url(self, event):
        sel = self.results_listbox.curselection()
        if not sel: return
        
        selected_text = self.results_listbox.get(sel[0])
        
        if "Nenhum resultado encontrado" in selected_text or "Resultados para" in selected_text or "---" in selected_text or "Dica:" in selected_text:
            return

        match = re.search(r'\((https?:\/\/[^\)]+)\)', selected_text)
        if match:
            url = match.group(1)
            try:
                webbrowser.open_new_tab(url)
            except Exception as e:
                messagebox.showerror('Erro ao Abrir URL', f'Nao foi possivel abrir a URL: {url}\nErro: {e}')
        else:
            messagebox.showwarning('Link Invalido', 'Nao foi possivel extrair um link valido da selecao. Formato esperado: (url_aqui).')

    def _view_tree_structure(self):
        print("\n" + "="*70)
        # Texto sem emojis
        print("ESTRUTURA DA TRIE (ARVORE DE BUSCA)")
        print("Mapeamento de Palavras-Chave para Paginas Indexadas")
        print("="*70 + "\n")
        
        if not self.trie.root.children:
            print("A arvore esta vazia. Nenhuma pagina foi indexada ainda.")
            print("\n" + "="*70 + "\n")
            messagebox.showinfo('Arvore Vazia', 'A arvore esta vazia. Adicione algumas paginas primeiro para ver a estrutura no console.')
            return

        q = deque([(self.trie.root, '')]) # Usando deque para BFS
        printed_nodes_count = 0
        while q:
            node, path = q.popleft() # Usa popleft para BFS
            
            if node.pages:
                page_details = []
                for p in node.pages:
                    # Correção: p já é um objeto Page, então acessamos p.title e p.url diretamente
                    page_details.append(f"'{p.title}' <{p.url}>")
                print(f"Palavra: '{path}' -> Paginas: {', '.join(page_details)}")
                printed_nodes_count += 1
            
            for char_key in sorted(node.children.keys()):
                child_node = node.children[char_key]
                q.append((child_node, path + char_key))
        
        # Texto sem emojis
        print(f"\nTotal de {printed_nodes_count} nos com conteudo de pagina impressos.")
        print("\n" + "="*70 + "\n")
        messagebox.showinfo('Estrutura da Arvore', 'A estrutura detalhada da Trie foi impressa no console (saida padrao).')

    def _load_sample_data(self):
        samples = [
            Page('https://ifpe.edu.br/python-dev', 'Desenvolvimento Python no IFPE', 'python, desenvolvimento, web, ciencia de dados, automacao'),
            Page('https://ifpe.edu.br/estrutura-dados', 'Estruturas de Dados Essenciais para Algoritmos', 'estrutura de dados, algoritmos, arvores binarias, listas, pilhas, filas, grafos'),
            Page('https://ifpe.edu.br/algoritmos-analise', 'Analise de Complexidade de Algoritmos', 'analise, complexidade, algoritmos, tempo, espaco, otimizacao'),
            Page('https://ifpe.edu.br/web-aplicacoes', 'Criacao de Aplicacoes Web Modernas', 'aplicacoes web, flask, django, python, projetos, escalaveis')
        ]
        
        indexed_pages_count = 0
        for p in samples:
            keywords = [w.lower() for w in re.findall(r'\b\w{3,}\b', re.sub(r'[,;]', ' ', p.content))]
            for w in keywords:
                # Importante: self.trie.insert(w, p) já está adicionando o OBJETO Page 'p'
                self.trie.insert(w, p)
            indexed_pages_count += 1
        
        # Texto sem emojis
        print(f" {indexed_pages_count} paginas de exemplo carregadas e indexadas.")
        self._sample_pages = samples

    # --- Funcionalidades do Crawler ---

    def _update_crawler_log(self, message):
        self.crawler_log_text.config(state='normal')
        self.crawler_log_text.insert(tk.END, message + '\n')
        self.crawler_log_text.see(tk.END)
        self.crawler_log_text.config(state='disabled')
        self.root.update_idletasks()

    def _update_progress_bar(self, current, total):
        if total > 0:
            percentage = (current / total) * 100
            self.crawler_progress_bar['value'] = percentage
            self.crawler_progress_label.config(text=f'{int(percentage)}% Concluido ({current}/{total} paginas processadas)')
        else:
            self.crawler_progress_bar['value'] = 0
            self.crawler_progress_label.config(text='0% Concluido')
        self.root.update_idletasks()

    def _start_crawling(self):
        start_url = self.crawler_url_entry.get().strip()
        depth_str = self.crawler_depth_entry.get().strip()

        if start_url == 'Ex: https://ifpe.edu.br': start_url = ''
        if depth_str == '1': pass
        
        if not start_url:
            messagebox.showwarning('URL de Inicio Vazia', 'Por favor, insira uma URL para iniciar o crawling.')
            return

        if not re.match(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', start_url):
            messagebox.showerror('URL Invalida', 'Por favor, insira uma URL de inicio valida (ex: https://ifpe.edu.br).')
            return

        try:
            max_depth = int(depth_str)
            if max_depth < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Profundidade Invalida', 'Por favor, insira um numero inteiro nao negativo para a profundidade.')
            return

        self.crawler_log_text.config(state='normal')
        self.crawler_log_text.delete('1.0', tk.END)
        self.crawler_log_text.config(state='disabled')
        self._update_progress_bar(0, 0)
        self.visited_urls.clear()

        self._update_crawler_log(f"Iniciando crawling a partir de: {start_url} (Profundidade: {max_depth})")
        self.root.after(100, lambda: self._simple_web_crawler(start_url, max_depth))

    def _simple_web_crawler(self, start_url, max_depth):
        queue = deque([(start_url, 0)])
        
        pages_processed = 0
        total_pages_to_process = 1

        while queue:
            current_url, current_depth = queue.popleft()

            if current_url in self.visited_urls:
                continue

            self.visited_urls.add(current_url)
            self._update_crawler_log(f"Processando: {current_url} (Profundidade: {current_depth})")
            pages_processed += 1
            self._update_progress_bar(pages_processed, total_pages_to_process)

            try:
                response = requests.get(current_url, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                page_title = soup.title.string if soup.title else 'Titulo Desconhecido'
                
                page_content_paragraphs = [p.get_text() for p in soup.find_all('p')]
                page_content = ' '.join(page_content_paragraphs).strip()

                if page_content:
                    words_indexed = self._add_page_to_trie(current_url, page_title, page_content)
                    self._update_crawler_log(f"   > Indexado: '{page_title}' ({words_indexed} palavras)")
                else:
                    self._update_crawler_log(f"   > '{page_title}' nao possui conteudo de paragrafo para indexar.")

                if current_depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        full_url = requests.compat.urljoin(current_url, href)
                        
                        if re.match(r'^https?:\/\/', full_url) and requests.utils.urlparse(full_url).netloc == requests.utils.urlparse(start_url).netloc:
                            # CORREÇÃO: A fila deve armazenar tuplas (url, depth), não objetos Page
                            # Mas a verificação de duplicatas na fila precisa ser precisa
                            if full_url not in self.visited_urls and all(u[0] != full_url for u in queue): 
                                queue.append((full_url, current_depth + 1))
                                total_pages_to_process += 1
                                self._update_progress_bar(pages_processed, total_pages_to_process)

            except requests.exceptions.RequestException as e:
                self._update_crawler_log(f"   > Erro ao acessar {current_url}: {e}")
            except Exception as e:
                self._update_crawler_log(f"   > Erro inesperado ao processar {current_url}: {e}")
            
            self.root.update_idletasks() 
            self.root.after(50)

        self._update_crawler_log("Crawling concluido!")
        self._update_progress_bar(pages_processed, pages_processed)
        messagebox.showinfo('Crawling Concluido', f'O crawling terminou. {pages_processed} paginas processadas e indexadas.')

if __name__ == '__main__':
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()