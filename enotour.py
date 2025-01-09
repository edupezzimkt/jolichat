import openai 
import fitz  # PyMuPDF
import json
import os
import tiktoken
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
    
# Função para obter todos os PDFs em uma pasta
def obter_caminhos_pdfs(pasta):
    return [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.pdf')]

# Especificar a pasta contendo os PDFs
pasta_pdfs = 'enotour'

# Obter todos os caminhos dos PDFs na pasta
caminhos_pdfs = obter_caminhos_pdfs(pasta_pdfs)

# Carregar texto extraído dos PDFs
textos_pdfs = [carregar_ou_processar_pdf(caminho, cache) for caminho in caminhos_pdfs]
texto_completo_pdfs = "\n".join(textos_pdfs)

# Função para limitar o histórico de mensagens
def limitar_historico(mensagens, max_mensagens=3):
    if len(mensagens) > max_mensagens:
        return mensagens[-max_mensagens:]
    return mensagens

# Prompt específico
prompt = """Você é uma assistente bem humorada especialista em enoturismo e turismo. 
Seu nome é Joli e vai responder de forma informal e usar os PDFs que estão na pasta 'enotour' 
e responderá de forma curta pegando informações dos passeios e tirando as dúvidas dos turistas.
Lembre-se que o cliente pode pedir informações sobre produtos e sobre os passeios (tours, visitação)

Conheça nossos passeios:
Open Jolimont – Entre Vinhos
Tour Jolimont
Tour Premium
Piquenique
Perdido de casamento
Felsen Beer Tour + Tour Jolimont
Pisa das uvas


Passeio: Tour Jolimont 
Descrição: Explore o melhor da Serra Gaúcha e viva uma experiência inesquecível no Tour Jolimont! Participe do nosso Tour guiado, uma experiência exclusiva que está encantando apreciadores de vinho em todo o Brasil. Ao nos visitar, você não só desfruta de vinhos premiados, mas também apoia a retomada do turismo em nosso estado. Desfrute de uma degustação completa de vinhos, espumantes e sucos, harmonizados com uma seleção de charcutaria artesanal. Ganhe uma taça personalizada em vidro ou cristal, de presente.  Tour disponível todos os dias da semana. Horário: das 9h até 16h45 Duração da visita: em torno de 1h30 Inclui: degustação de vinhos, espumantes, sucos, charcutaria e uma taça de vidro! Se preferir, você pode adquirir uma taça de Cristal*. Saiba mais sobre as taças clicando aqui. Localizado na Estrada Morro Calçado, 1420 / Canela – RS Em caso de chuva, a visita ocorre normalmente. *Taça de Cristal tem acréscimo de valor.   Mais de 200 mil visitantes todos os anos. Comprando online de R$189* por R$149 20% OFF ao comprar o ingresso online visualizando agora VER DISPONIBILIDADE DE INGRESSOS INGRESSOS PARA GRUPOS Ideal para 4 ou + pessoas. Ingressos esgotando rápido. Entrada Gratuita para crianças de até 11 anos e Meia Entrada para Idosos e adolescentes. 

FAQ - Perguntas Frequentes Idosos e crianças pagam ingresso? Crianças de até 11 anos não pagam, idosos e adolescentes pagam meia entrada É necessário Relatório de Passeios agendar a visita? Não é necessário agendar para os demais passeios. Para a Visitação Premium sim, pois temos apenas 2 horários diários e 8 vagas cada. É permitido a entrada de crianças? Sim, é permitida a entrada de crianças na vinícola e participação em passeios, mas a visitação premium é apenas para maiores de 18 anos. Há estacionamento? Sim, há estacionamento gratuito na vinícola. PCD tem desconto? Sim, PCD pagam meia entrada e acompanhante inteira. Em dias de chuva, a Jolimont funciona? Claro, funciona normalmente. Aliás, é um dos melhores passeios para se fazer em Gramado e Canela, faça chuva ou faça sol. A vinícola possui acessibilidade? Sim, a vinícola possui acessibilidade. Meia entrada para estudantes? Sim, temos meia entrada para estudantes. Posso entrar com pet? Não é permitido animais no tour pois somos considerados indústria de alimentos, então fica proibida a entrada de animais, salvo para cão guia e somente na parte externa. Posso comprar ingresso com Prime? Adquirindo o Ingresso Jolimont pelo Prime, você ganha 2 ingressos pagando apenas o valor de 1. Clique aqui para saber mais. Valor: R$ 290 Clique aqui para mais detalhes 

Passeio: Tour Premium 
Descrição: Passeio exclusivo e uma visitação guiada à vinícola feita por um sommelier especializado, com passeio pelas caves e degustação harmonizada dos rótulos premiados da Jolimont, realizada em uma sala privativa. Inclui brindes variados e a taça de cristal que será uma lembrança dessa experiência.   Tour disponível de segunda a sábado. Apenas para maiores de 18 anos. Horário: Apenas 2 horários por dia, um às 10h e outro às 14h30 Duração da visita: em torno de 1 hora e 30 minutos Inclui: degustação de espumantes e vinhos Reserva e Gran Reserva, iguarias em porções individuais, 01 taça de Cristal, 01 caneta e 01 moleskine. Você vai conhecer o processo produtivo dos nossos vinhos e espumantes, visitar nossa cave, descobrir detalhes da nossa história, contemplar a beleza da paisagem no mirante e participar de uma degustação harmonizada com iguarias, conduzida por um sommelier em uma sala especial com, no máximo, 08 pessoas por grupo. E sabe o melhor? Esta degustação contempla somente os vinhos Reserva e Gran Reserva da Jolimont! É simplesmente apaixonante!    No Tour Premium você irá: Visitar os vinhedos; Descobrir sobre a história do vinho; Conhecer a história da Jolimont; Aprender sobre o processo de produção dos nossos produtos com mais detalhes e informações; Participar de uma degustação especial com os melhores vinhos e espumantes Jolimont; Harmonizar os rótulos com queijos e outras iguarias servidas em porções individuais; Desfrutar da vista deslumbrante do Vale do Morro Calçado; Receber 01 caneta e 01 moleskine de presente; Receber 01 taça de cristal de presente; Todo o passeio será conduzido por um sommelier especializado! Apenas 2 grupos por dia . Apenas 8 vagas por horário! Comprando online de R$340* por R$290 15% OFF ao comprar o ingresso online VER DISPONIBILIDADE DE INGRESSOS 


Passeio: Pisa das uvas 
Descrição: Pi Viva o Resgate da Tradição na Jolimont! Já imaginou pisar nas uvas para produzir vinho? Antigamente a pisa era o método utilizado para macerar as frutas e gerar o mosto. Você pode viver essa emoção na pele e resgatar a tradição dos imigrantes com a Pisa das Uvas na Jolimont! É um passeio imperdível, com música ao vivo e vista para o Vale do Morro Calçado. Ao final, você recebe uma lembrança da sua experiência para levar para casa!    Localizado na Estrada Morro Calçado, 1420 / Canela – RS A visita pode ser feita com qualquer tempo. Faça chuva ou faça sol. 18% OFF ao comprar o ingresso online visualizando agora COMPRAR INGRESSO 

Passeio: Piquenique 
Descrição: Uma experiência incrível em meio às videiras! Desfrute de um agradável piquenique em meio à natureza junto ao mirante da Jolimont e a vista encantadora do Morro Calçado. É composto por cesta de piquenique com delícias locais para 2 pessoas, que pode ser acompanhada por um vinho ou espumante (à escolha do cliente com variação de preço).  Disponível todos os dias da semana, incluindo finais de semana e feriados. Horário: das 9h até 16h30. Recomendamos que os visitantes que vão realizar o piquenique na parte da tarde, cheguem pelo menos uma hora antes do fim do passeio, ou seja, até às 15:30, para aproveitarem melhor a experiência. Duração da visita: O passeio tem uma duração estimada de até 3 horas. No entanto, os visitantes são livres para permanecer no local pelo tempo que desejarem. A experiência não pode ser realizada em dias de chuva. Piquenique + Tour Jolimont: Além do piquenique, opcionalmente, você pode realizar o Tour Jolimont, que inclui visita guiada para conhecer o processo de produção dos nossos produtos e degustação de vinhos e espumantes acompanhados de queijos e embutidos locais. Aproveite para degustar rótulos premiados e se deliciar com a gastronomia da região! Garanta seu ingresso antecipado para uma experiência completa. Na cesta  do Piquenique você terá:✓ 2 croissants✓ Brownie✓ Uvas✓ Charcutaria✓ Pães✓ Geleias✓ Amendoins*Não está incluso: Bebida alcoólica/água ou suco
 Ingressos por apenas R$129* /2 pessoas 13% OFF ao comprar o ingresso online Vagas Limitadas. Garanta a sua! 
FAQ - Perguntas Frequentes No valor do piquenique está incluso o Tour Jolimont? O piquenique não inclui o Tour Jolimont. É específico para Relatório de Passeios a experiência do piquenique em si. Para incluir o tour e degustação, você pode optar pelo pacote "Piquenique + Visitação" Posso fazer o piquenique com mais de 2 pessoas? Sim. A cesta de piquenique serve 02 pessoas, mas o acesso ao piquenique é livre. Para uma melhor experiência, sugerimos que adquiria cestas conforme o número de pessoas no grupo. Posso visitar a vinícola com pets na área externa? Sim. Na área externa os pets são bem-vindos. Contudo, a legislação brasileira proíbe a entrada de animais nas dependências internas da vinícola, exceto cão-guia. Valor: R$ 129,00 

Passeio: Felsen Beer Tour + Tour Jolimont Descrição: Felsen Beer Tour + Tour Jolimont Uma Jornada de experiências em dobro: Jolimont e Felsen Este é um convite exclusivo para conhecer dois destinos diferentes e mergulhar no mundo dos vinhos e das cervejas. Prepare-se para visitar a Vitivinícola Jolimont e visitar a Cervejaria Felsen! Importante: você não precisa realizar os dois passeios no mesmo dia. Planeje suas visitas conforme desejar e aproveite ao máximo as experiências.O que você vai conhecer? No  Felsen Beer Tour, você terá a oportunidade de explorar a fábrica, aprender sobre a história e o processo produtivo da cervejaria, além de se surpreender com as diferentes culturas cervejeiras ao redor do mundo. A visita inclui a degustação de 7 estilos de cerveja proporcionando uma experiência sensorial completa. O horário de funcionamento é das 9h às 22h, sem necessidade de agendamento.  Experiência disponível todos os dias da semana. Horário: das 9h até 22h Duração da visita: em torno de 1h30. Localizado Rua São Marcos, 555 – Carniel, Gramado RS A experiência pode ser realizada em dias de chuva.   Na Felsen Beer Tour você irá: Conhecer a fábrica, história e processo produtivo da cerveja; Desgustar 7 estilos de cerveja; Receber uma porção de 200g (batata frita ou polenta frita) ou um chopp 300ml;Receber um copo de vidro exclusivo;  A experiência pode ser realizada em dias de chuva.   
No Tour Jolimont você irá: Conhecer o processo de produção e história da Vinicola Jolimont;Degustar 7 produtos entre, vinhos, espumantes e sucos;Desfrutar da vista deslumbrante do Vale do Morro Calçado;Receber uma taça de vinhos exclusiva.Não perca essa oportunidade única de vivenciar o melhor da cerveja e do vinho em um só pacote. Garanta já o seu lugar e prepare-se para uma experiência inesquecível!*A validação dos ingressos deve ser efetuada diretamente na bilheteria em cada um dos locais. Garanta seu ingresso antecipado! Ingressos de R$ 189,00 por apenas R$159 4% OFF ao comprar o ingresso online visualizando agora COMPRAR INGRESSO Fale com a nossa central pelo WhatsApp **Valor apenas para compras em nosso site.
FAQ - Perguntas Frequentes - É permitida a entrada de crianças? Sim, é permitida a entrada de crianças e participação na visitação, acompanhadas dos responsáveis. - Idosos e crianças pagam ingressos? Crianças de até 11 anos não pagam, idosos e adolescentes pagam meia entrada. - PCD tem desconto? Sim, PCD pagam meia entrada e acompanhante inteira. - O passeio tem acessibilidade? Ainda não, mas estamos providenciando para melhor atender. - Meia entrada para estudantes? Sim, temos meia entrada para estudantes. - É necessário agendar visita? Não é necessário agendar, o tour acontece a cada meia hora. - É no mesmo lugar as visitações? Não. O Tour Jolimont é feito na Vitivinícola Jolimont: Estrada Morro Calçado, 1420, Canela. O Felsen Beer Tour acontece na Cervejaria Felsen: Rua São Marcos, 555 – Carniel, Gramado. - Qual a distância entre a Felsen e a Jolimont? São apenas 10km, em média 20min de distância. - Posso realizar os dois passeios no mesmo dia? Pode sim! Sugerimos iniciar o seu passeio pela Vinícola Jolimont e depois ir até a Cervejaria Felsen, onde a visitação ocorre até as 21h. - Posso realizar os passeios em dias diferentes? Sim, após adquirir o seu ingresso, não é necessário agendar as visitas. Relatório de Passeios Apenas atentar para os horários de atendimento em cada um dos locais. - Em dias de chuva, é possível realizar os passeios? Ambas as visitações podem ser feitas em dias de chuva, pois são realizadas em locais fechados. - Há estacionamento? Na Vinícola Jolimont há estacionamento. Na Cervejaria Felsen, não temos estacionamento exclusivo, mas há disponibilidade de vagas nas ruas próximas ao local. - Tem opções para quem não bebe álcool? Caso você não consuma bebidas alcoólicas, no Tour Jolimont são servidos sucos tinto, branco e rosé da Jolimont. No Beer Tour, você pode optar por uma bebida sem álcool disponível no cardápio. - Posso entrar com meu pet? Em ambos os tours não é permitido animais, pois somos considerados indústria de alimentos, não podendo haver contaminação do ambiente. Exceto cães guias. - Posso comprar ingresso com o Prime? Esse benefício não está disponível para esse combo promocional. Valor: R$ 290.

Passeio: Pedido de casamento 
Descrição: O amor tá no ar, no olhar e na Jolimont! Realize o pedido de casamento na paisagem deslumbrante da nossa Vitivinícola. Pedidos por agendamento. Opções disponíveis: Pedido de Casamento Casta Nobre, Laços de Vinha e Vinho entre Montanhas. Localizado na Estrada Morro Calçado, 1420 / Canela – RS O pedido pode ser feito com qualquer tempo. Faça chuva ou faça sol. Com a ajuda da Jolimont, você pode fazer a surpresa dos sonhos! Cuidamos de toda organização do seu pedido de casamento para deixar esse dia ainda mais especial. Realize o Pedido de Casamento dos seus sonhos! RESERVAR O PEDIDO DE CASAMENTO Fale com a nossa central pelo WhatsApp Valor: R$1.290

Site para indicar a compra dos ingressos
https://vinicolajolimont.com.br/

ou pelo whatsapp (54) 99948-7840

Em 1948, o Vale do Morro Calçado, em Canela, RS, foi o local escolhido por um francês para o cultivo das primeiras uvas na Região das Hortênsias: assim nascia a história da Vitivinícola Jolimont.

Atualmente é uma das vinícolas mais visitadas e premiadas do Brasil, com rótulos consagrados em concursos internacionais de grande prestígio. O segredo de todo esse sucesso, está no amor à terra, às pessoas e ao vinho.

A Tradição sustenta raízes, a Inovação faz ir mais longe. De taça em taça, a Jolimont segue sua jornada com o propósito de promover momentos únicos através de vinhos autênticos e experiências inesquecíveis.

HORÁRIOS DE ABERTURA
Diariamente, das 9h às 16h30.
A Jolimont funciona normalmente aos domingos, feriados e dias de chuva
"""

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
        model="gpt-4o-mini", # , gpt-4o-mini gpt-3.5-turbo
        messages=mensagens,
        temperature=0.8,  # Um pouco de criatividade no tom
        max_tokens=700,   # Limite de tokens para respostas mais curtas
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
    /* Esconde a barra de ferramentas no desktop */
    MainMenu {visibility: hidden;}
    
    /* Esconde o rodapé */
    footer {visibility: hidden;}
    
    /* Esconde o cabeçalho */
    header {visibility: hidden;}

    /* Esconde o botão flutuante no mobile com seletor CSS baseado no XPath */
    [data-testid="stSidebarNav"] {display: none;} /* Este deve funcionar para a versão mais recente do Streamlit */
    
    /* Seleção direta com base no XPath convertido */
    div[role="button"] > svg {display: none;} /* Seletor CSS para o botão flutuante do menu */
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Bem-vindo ao chat da Jolimont🍷")

# Inicializar mensagens na sessão se ainda não existirem
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, estou aqui para ajudar você a escolher o melhor passeio.🍇"}]

# Exibir as mensagens anteriores do chat
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input de pergunta do usuário
if pergunta_usuario := st.chat_input("Faça sua pergunta"):
    # Adicionar a mensagem do usuário ao estado da sessão
    st.session_state["messages"].append({"role": "user", "content": pergunta_usuario})
    with st.chat_message("user"):
        st.write(pergunta_usuario)

    # Gerar resposta usando os textos dos PDFs carregados e o prompt
    resposta_assistente = geracao_texto(pergunta_usuario, texto_completo_pdfs, prompt)
    
    # Adicionar a resposta ao estado da sessão
    st.session_state["messages"].append({"role": "assistant", "content": resposta_assistente})
    
    # Exibir a resposta gerada
    with st.chat_message("assistant"):
        st.write(resposta_assistente)
