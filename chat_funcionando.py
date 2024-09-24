import openai 
import fitz  # PyMuPDF
import json
import os
import tiktoken
import streamlit as st

# Carregar a chave da OpenAI dos secrets do Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

class Chat:
    def __init__(self):
        # Inicializa o chat
        pass

    def get_response(self, message):
        # Processa a mensagem e retorna uma resposta
        return "Resposta do chat"
    
# Função para extrair texto do PDF
def extrair_texto_pdf(caminho_pdf):
    documento = fitz.open(caminho_pdf)
    texto_completo = ""
    for pagina in documento:
        texto_completo += pagina.get_text()
    return texto_completo

# Função para carregar cache de um arquivo JSON
def carregar_cache(nome_arquivo):
    if os.path.exists(nome_arquivo):
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo)
        except json.JSONDecodeError:
            print(f"Erro ao carregar o cache de {nome_arquivo}. O arquivo está corrompido.")
    return {}

# Função para salvar cache em um arquivo JSON
def salvar_cache(cache, arquivo):
    # Converte as chaves do dicionário para strings
    cache_convertido = {str(k): v for k, v in cache.items()}
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(cache_convertido, f, ensure_ascii=False, indent=4)

# Inicializa o cache
cache_arquivo = 'cache.json'
cache = carregar_cache(cache_arquivo)

# Carregar texto extraído dos PDFs com cache
def carregar_ou_processar_pdf(caminho_pdf, cache):
    if caminho_pdf in cache:
        print(f"Carregado do cache: {caminho_pdf}")
        return cache[caminho_pdf]
    texto_pdf = extrair_texto_pdf(caminho_pdf)
    cache[caminho_pdf] = texto_pdf
    salvar_cache(cache, cache_arquivo)
    return texto_pdf

# Função para obter todos os PDFs em uma pasta
def obter_caminhos_pdfs(pasta):
    return [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.pdf')]

# Especificar a pasta contendo os PDFs
pasta_pdfs = 'arquivos'

# Obter todos os caminhos dos PDFs na pasta
caminhos_pdfs = obter_caminhos_pdfs(pasta_pdfs)

# Carregar texto extraído dos PDFs
textos_pdfs = [carregar_ou_processar_pdf(caminho, cache) for caminho in caminhos_pdfs]
texto_completo_pdfs = "\n".join(textos_pdfs)

# Função para dividir o texto em partes menores
def dividir_texto(texto, max_tokens):
    palavras = texto.split()
    partes = []
    parte_atual = []
    tokens_atual = 0

    for palavra in palavras:
        tokens_palavra = len(palavra) // 4  # Estimativa de tokens
        if tokens_atual + tokens_palavra > max_tokens:
            partes.append(" ".join(parte_atual))
            parte_atual = []
            tokens_atual = 0
        parte_atual.append(palavra)
        tokens_atual += tokens_palavra

    if parte_atual:
        partes.append(" ".join(parte_atual))

    return partes

# Dividir o texto completo em partes menores
max_tokens = 1000  # Ajuste conforme necessário
partes_texto = dividir_texto(texto_completo_pdfs, max_tokens)

# Função para gerar respostas a partir das partes de texto
def gerar_respostas(partes_texto, prompt):
    respostas = []
    for parte in partes_texto:
        mensagens = [
            {"role": "system", "content": "Você é um especialista em turismo e vinhos da vinícola Jolimont. Responda de forma leve e moderna"},
            {"role": "user", "content": parte + "\n\n" + prompt}
        ]
        resposta = openai.ChatCompletion.create(
            model="gpt-o1-preview",
            messages=mensagens
        )
        respostas.append(resposta['choices'][0]['message']['content'])
    return respostas


def contar_tokens(texto):
    enc = tiktoken.get_encoding('cl100k_base')
    return len(enc.encode(texto))

def geracao_texto(mensagens, contexto, prompt):
    chave_cache = tuple((mensagem['role'], mensagem['content']) for mensagem in mensagens)
    
    if chave_cache in cache:
        resposta_cache = cache[chave_cache]
        print("Joli (from cache): ", resposta_cache)
        mensagens.append({'role': 'assistant', 'content': resposta_cache})
        return mensagens
    
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role': 'system', 'content': prompt}] + mensagens + [{'role': 'system', 'content': contexto}],
        temperature=0,
        max_tokens=800,
    )

    print('Joli: ', end='')
    texto_completo = ''

    for resposta_stream in resposta['choices']:
        texto = resposta_stream['message']['content']
        if texto:
            print(texto, end='')
            texto_completo += texto
    print()
    
    mensagens.append({'role': 'assistant', 'content': texto_completo})
    cache[chave_cache] = texto_completo  # Armazena a resposta no cache
    salvar_cache(cache, cache_arquivo)  # Salva o cache em disco
    
    return mensagens

# Streamlit interface
st.title("Bem-vindo ao chat da Jolimont🍷 :)")

mensagens = []
prompt = """Você é um assistente bem humorado especialista em turismo. 
Seu nome é Joli e vai usar os PDFs que estão na pasta 'arquivos' e responderá de forma 
curta pegando informações dos passeios e tirando as dúvidas dos turistas."""

input_usuario = st.text_input('Faça sua pergunta:', '')

if st.button('Enviar'):
    if input_usuario:
        mensagens.append({'role': 'user', 'content': input_usuario})
        mensagens = geracao_texto(mensagens, texto_completo_pdfs, prompt)
        for mensagem in mensagens:
            if mensagem['role'] == 'assistant':
                st.write(f"Joli: {mensagem['content']}")
