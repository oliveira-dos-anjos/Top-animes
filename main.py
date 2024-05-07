import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request


# Criação da instância do Flask
app = Flask(__name__)

# URL da página
url = 'https://myanimelist.net/topanime.php'
response = requests.get(url)


# Obtém o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define o caminho para a pasta static/imagens_animes
IMAGENS_ANIMES_PATH =  'static/imagens_animes'

# Função para limpar caracteres inválidos para nomes de arquivo
def limpar_nome_arquivo(nome):
    return re.sub(r'[\\/*?:"<>|]', '_', nome)


def obter_lista_animes():

    if response.status_code == 200:

        html_content = response.text    
        
        soup = BeautifulSoup(html_content, 'html.parser')

        top_ranking_tables = soup.find_all('table', class_='top-ranking-table')

        lista_anime = []
        for top_ranking_table in top_ranking_tables:
            for row in top_ranking_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    Rank = cells[0].get_text().strip()
                    title_h3 = cells[1].find('h3')
                    title = title_h3.get_text().strip() if title_h3 else "TITULO"
                    Score = cells[2].get_text().strip()

                    # Usando a função para limpar o título do anime
                    title_cleaned = limpar_nome_arquivo(title)

                    # Obtém o caminho da imagem para o anime atual
                    imagem_anime_path = os.path.join(IMAGENS_ANIMES_PATH, f'{title_cleaned}.jpg')
            

                    # Verifica se a imagem já foi baixada
                    if not os.path.exists(imagem_anime_path):
                        # Cria o diretório se não existir
                        os.makedirs(IMAGENS_ANIMES_PATH, exist_ok=True)

                        # Encontra o URL da imagem na página
                        img = cells[1].find('img', {'data-src': True})
                        if img:
                            url_imagem = img['data-src']
                            try:
                                # Baixa a imagem e salva-a na pasta de imagens
                                response_img = requests.get(url_imagem)
                                with open(imagem_anime_path, 'wb') as f:
                                    f.write(response_img.content)
                            except Exception as e:
                                print(f"Erro ao baixar a imagem: {e}")
                                continue       
                                
                    
                    # Normalizar o caminho (remover o prefixo static)
                    imagem_anime_path = imagem_anime_path.replace('\\', '/')
                    print(f"\033[34m{imagem_anime_path}")

                    lista_anime.append({'rank': Rank, 'title': title, 'score': Score, 'imagem_path': imagem_anime_path})

   
                    
        return lista_anime[1:]

    else:
        return [{'rank': '', 'title': 'Erro de Requisição', 'score': ''}]


# Rota para a página inicial
@app.route('/')
def home():
    # Chama a função para obter a lista de animes
    lista_animes = obter_lista_animes()

     # Modifica o caminho da imagem antes de renderizar o template
    for anime in lista_animes:
        anime['imagem_path'] = anime['imagem_path'].replace('static/imagens_animes/', '')

        
        print(f'\033[32m{anime["imagem_path"]}')

    # Renderiza o template HTML e passa a lista de animes como contexto
    return render_template('index.html', lista_animes=lista_animes)


# Inicia o aplicativo Flask
if __name__ == "__main__":
    app.run(debug=True)

