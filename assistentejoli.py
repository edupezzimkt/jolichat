import openai
import fitz  # PyMuPDF
import json
import os
import tiktoken
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Carregar a chave da OpenAI dos secrets do Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
    cache_convertido = {str(k): v for k, v in cache.items()}
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(cache_convertido, f, ensure_ascii=False, indent=4)

# Função para extrair texto de um site
def extrair_texto_site(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        sopa = BeautifulSoup(resposta.text, "html.parser")
        # Extrair texto de tags relevantes (exemplo: `<p>` e `<h1>`)
        texto = " ".join([tag.get_text(strip=True) for tag in sopa.find_all(['p', 'h1', 'h2', 'h3'])])
        return texto
    except Exception as e:
        print(f"Erro ao acessar o site {url}: {e}")
        return ""

# Inicializa o cache
cache_arquivo = 'cache.json'
cache = carregar_cache(cache_arquivo)

# Carregar texto extraído dos PDFs com cache
def carregar_ou_processar_pdf(caminho_pdf, cache, max_tokens=1000):
    if caminho_pdf in cache:
        return cache[caminho_pdf]
    texto_pdf = extrair_texto_pdf(caminho_pdf)
    texto_pdf = texto_pdf[:max_tokens]  # Limita o tamanho do texto para evitar ultrapassar os tokens
    cache[caminho_pdf] = texto_pdf
    salvar_cache(cache, cache_arquivo)
    return texto_pdf

# Carregar texto extraído dos sites com cache
def carregar_ou_processar_site(url, cache):
    if url in cache:
        return cache[url]
    texto_site = extrair_texto_site(url)
    cache[url] = texto_site
    salvar_cache(cache, cache_arquivo)
    return texto_site

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

# URLs dos sites
urls_sites = [
    "https://www.vinhosjolimont.com.br/",
    "https://vinicolajolimont.com.br/"
]

# Carregar texto extraído dos sites
textos_sites = [carregar_ou_processar_site(url, cache) for url in urls_sites]
texto_completo_sites = "\n".join(textos_sites)

# Combinar textos dos PDFs e dos sites
texto_contexto_completo = f"{texto_completo_pdfs}\n\n{texto_completo_sites}"

# Função para limitar o histórico de mensagens
def limitar_historico(mensagens, max_mensagens=3):
    if len(mensagens) > max_mensagens:
        return mensagens[-max_mensagens:]
    return mensagens

# Prompt específico
prompt = """Você é uma assistente bem humorada especialista em turismo e um sommelier internacional. 
Seu nome é Joli e vai responder de forma informal e usar as informações disponíveis. 
Responda de forma curta pegando informações dos passeios, produtos e tirando as dúvidas dos turistas. 
Quando a conversa for sobre produtos, direcione para informações dos produtos e contatos, 
e quando for sobre turismo, utilize informações dos passeios."""

# Função para geração de texto usando o contexto e o prompt
def geracao_texto(pergunta_usuario, contexto, prompt):
    chave_cache = (pergunta_usuario,)

    if chave_cache in cache:
        resposta_cache = cache[chave_cache]
        return resposta_cache

    # Montar a mensagem com o prompt e contexto
    mensagens = [
        {"role": "system", "content": prompt + "\n\n" + contexto},
        {"role": "user", "content": pergunta_usuario}
    ]
    
    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Modelos: gpt-4o-mini ou gpt-3.5-turbo
        messages=mensagens,
        temperature=0.5,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0.6,
    )

    texto_resposta = resposta['choices'][0]['message']['content']
    
    # Adicionar a resposta ao cache
    cache[chave_cache] = texto_resposta
    salvar_cache(cache, cache_arquivo)
    
    return texto_resposta

# Streamlit interface

# CSS para esconder o botão flutuante no mobile usando seletor mais específico
hide_streamlit_style = """
    <style>
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Bem-vindo ao chat da Jolimont🍷")

# Inicializar mensagens na sessão se ainda não existirem
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, estou aqui para responder sobre produtos e passeios.🍇"}]

# Exibir as mensagens anteriores do chat
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input de pergunta do usuário
if pergunta_usuario := st.chat_input("Faça sua pergunta"):
    st.session_state["messages"].append({"role": "user", "content": pergunta_usuario})
    with st.chat_message("user"):
        st.write(pergunta_usuario)

    resposta_assistente = geracao_texto(pergunta_usuario, texto_contexto_completo, prompt)
    st.session_state["messages"].append({"role": "assistant", "content": resposta_assistente})
    with st.chat_message("assistant"):
        st.write(resposta_assistente)
