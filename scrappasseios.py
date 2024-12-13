import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from fpdf import FPDF

# Função para extrair informações de passeios
def extrair_informacoes_passeios(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    titulos = []
    descricoes = []
    valores = []
    links = []

    atracoes = soup.find_all('article', class_='item card-passeio')

    for atracao in atracoes:
        titulo = atracao.find('h3').text.strip()
        link_saiba_mais = atracao.find('a', class_='bt-primary bt-saiba')['href']
        link_saiba_mais = urljoin(url, link_saiba_mais)
        
        detalhes_response = requests.get(link_saiba_mais)
        detalhes_html = detalhes_response.text
        detalhes_soup = BeautifulSoup(detalhes_html, 'html.parser')
        
        descricao_div = detalhes_soup.find('section', class_='fleft100 pg-passeio')
        descricao = descricao_div.text.strip() if descricao_div else "Descrição não encontrada"
        
        valor_div = detalhes_soup.find('span', class_='valor')
        valor = valor_div.text.strip() if valor_div else "Valor não encontrado"
        
        titulos.append(titulo)
        descricoes.append(descricao)
        valores.append(valor)
        links.append(link_saiba_mais)

    return pd.DataFrame({'Título': titulos, 'Descrição': descricoes, 'Valor': valores, 'Link': links})

# Função para extrair informações da página "A Jolimont"
def extrair_informacoes_jolimont(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Tentar encontrar o elemento correto
    descricao_div = soup.find('div', class_='fleft100 content-sobre')
    if descricao_div:
        descricao_jolimont = descricao_div.text.strip()
    else:
        descricao_jolimont = "Informações sobre a Jolimont não encontradas."

    return descricao_jolimont

# URL da página principal com as atrações
url_passeios = "https://vinicolajolimont.com.br/nossos-passeios/"

# URL da página "A Jolimont"
url_jolimont = "https://vinicolajolimont.com.br/a-jolimont/"

# Extraindo as informações dos passeios
df_passeios = extrair_informacoes_passeios(url_passeios)

# Extraindo as informações da página "A Jolimont"
descricao_jolimont = extrair_informacoes_jolimont(url_jolimont)

# Classe PDF personalizada usando fonte Unicode
class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', '', 12)
        self.cell(0, 10, 'Relatório de Passeios', align='C', ln=True)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

    def add_link(self, text, url):
        self.set_font('DejaVu', 'U', 12)
        self.set_text_color(0, 0, 255)
        self.cell(0, 10, text, ln=True, link=url)
        self.set_text_color(0, 0, 0)
        self.ln()

# Crie uma instância do PDF
pdf = PDF()

# Adicionar a fonte Unicode (Baixe e adicione o arquivo TTF correto)
pdf.add_font('DejaVu', '', "C:/Users/eduar/OneDrive/documentos/Clientes/Jolimont/chat/dejavu-sans/ttf/DejaVuSans.ttf", uni=True)  # Altere o caminho para onde a fonte foi salva
pdf.add_font('DejaVu', 'B', "C:/Users/eduar/OneDrive/documentos/Clientes/Jolimont/chat/dejavu-sans/ttf/DejaVuSans.ttf", uni=True)  # Fonte bold

# Adicionar as informações da página "A Jolimont" ao PDF
pdf.add_chapter('A Jolimont', descricao_jolimont)

# Adicionar capítulos dos passeios ao PDF com links
for index, row in df_passeios.iterrows():
    pdf.add_chapter(row['Título'], f"Descrição: {row['Descrição']}\n\nValor: {row['Valor']}")
    pdf.add_link('Clique aqui para mais detalhes', row['Link'])

# Salvar o PDF
pdf_file_path = "passeios_jolimont.pdf"
pdf.output(pdf_file_path)

print(f"PDF salvo com sucesso em: {pdf_file_path}")