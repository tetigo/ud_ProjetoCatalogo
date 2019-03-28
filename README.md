# Projeto Catalogo de Categorias Udacity


Projeto onde podemos criar categorias de coisas e dentro de cada categoria podemos cadastrar itens.

### 0. Antes da Instalação das Dependências do Projeto Seguir os Seguintes Passos:
Instalar [Python3](https://www.python.org/downloads/release/python-368/). A versão que utilizei foi python3 v3.6.8.

Criar Diretório com nome que desejar.

Dentro desse diretório abrir janela do DOS rodando o comando CMD.

Rodar o comando para criar Ambiente Virtual do Python3:

```sh
python -m venv venv
```
Ativar o ambiente virtual para instalar programas necessários apenas nesse ambiente.
```sh
cd venv
cd Scripts
activate
cd ..
cd ..
```

### 1. Instalação:
```sh
pip install -r requirements.txt
```

### 2. Setar variaveis de ambiente
```sh
	set FLASK_APP=app.py
	set FLASK_ENV=development
```

### 3. Criar banco de dados:
```sh
flask db init
flask db migrate
flask db upgrade
```

### 4. Carregar dados iniciais para banco:
```sh
python carga_banco.py
```

### 5. Gerar Credenciais Google OAuth
Crie um projeto em: [developers.google.com](https://console.developers.google.com/)

Vá em Credenciais. Selecione Criar Credenciais -> ID do Cliente OAuth". 

Escolha Aplicativo da Web.

Na proxima pagina, tenha certeza de colocar http://localhost:5000 em Origens JavaScript autorizadas e http://localhost:5000/gCallback em URIs de redirecionamento autorizados.

Clique em salvar.

Pegue sua chaves: CLIENT_ID e CLIENT_SECRET

Crie um arquivo chamando ".flaskenv" sem as aspas mas com o ponto inicial.

Nesse arquivo coloque:
```sh
 CLIENT_ID='sua ID que acabou de salvar'
 CLIENT_SECRET='sua chave secreta que acabou de salvar'
 SECRET_KEY='chave secreta criada por você'
```
Coloque um em cada linha e salve o arquivo.

### 6. Para rodar digite:
```sh
flask run
```

### 7. Acesse no browser o endereço:
http://localhost:5000

### 8. Para acessar as APIS JSON:
http://localhost:5000/categorias.json

http://localhost:5000/nome_da_categoria/categoria.json

http://localhost:5000/items.json

http://localhost:5000/nome_do_item/items.json


Tiago Mendes
<tetigo@gmail.com>
