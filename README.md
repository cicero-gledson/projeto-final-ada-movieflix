# Projeto Final – MovieFlix Analytics

O MovieFlix Analytics é um projeto que demonstra uma plataforma simples para cadastro e avaliação de filmes. O objetivo é utilizar os dados gerados pelos usuários para realizar análises, como entender preferências e tendências de avaliações.

A aplicação foi desenvolvida para ser executada com Docker, e seu processo de build e publicação de imagens é automatizado por uma pipeline de CI/CD no GitHub Actions.

# Funcionalidades e Relatórios

Conforme as especificações do projeto, a plataforma foi desenvolvida para oferecer tanto funcionalidades de cadastro quanto de análise de dados.

### Ações Principais
A aplicação permite as seguintes operações de cadastro e avaliação de conteúdo:
* Cadastro de novos filmes no catálogo.
* Cadastro de usuários na plataforma.
* Envio de avaliações de um usuário para um filme.

### Relatórios Analíticos
A seção de análise simula um **Data Mart**, oferecendo cinco relatórios principais para gerar insights de negócio:

* **Top 10 Filmes por Gênero:** Exibe um ranking com os 10 filmes mais bem avaliados dentro de cada gênero, permitindo identificar os destaques do catálogo.

* **Nota Média por Faixa Etária:** Apresenta a nota média de cada filme, segmentada pelas faixas de idade dos usuários. Este relatório é ideal para direcionar recomendações e personalizar a experiência do usuário.

* **Número de Avaliações por País:** Mostra o total de avaliações realizadas por país, oferecendo um insight sobre o engajamento dos usuários em diferentes regiões.

* **5 Filmes Mais Populares:** Lista os cinco filmes que receberam o maior número de avaliações, indicando quais títulos estão gerando mais interesse na plataforma.

* **Melhor Avaliação Média por Gênero:** Classifica os gêneros de acordo com a sua nota média geral, ajudando a identificar as preferências do público para apoiar decisões de aquisição de conteúdo.

## Como Funciona

O projeto é dividido nos seguintes componentes principais que trabalham em conjunto:
* **Frontend:** Uma interface web (HTML/JS) com Nginx para exibir as informações e os relatórios.
* **API (Backend):** Um backend em Python/Flask que serve como ponte entre a interface e o banco de dados.
* **Banco de Dados:** Um banco de dados PostgreSQL para armazenar todos os dados da aplicação.
* **Importador (ETL):** Um script que carrega os dados iniciais de arquivos CSV para o banco na primeira inicialização do sistema.

---

## Como Executar o Projeto

Para rodar este projeto, é necessário ter o Git e o Docker Desktop instalados. Os passos abaixo detalham o processo.

### Pré-requisitos
* Git
* Docker Desktop (com Docker Compose)

### Passo a Passo

1.  **Clonar o projeto** para a máquina local:
    ```bash
    git clone [https://github.com/cicero-gledson/projeto-final-ada-movieflix.git](https://github.com/cicero-gledson/projeto-final-ada-movieflix.git)
    ```

2.  **Entrar na pasta** que foi criada:
    ```bash
    cd projeto-final-ada-movieflix
    ```

3.  **Subir a aplicação** com o Docker Compose:
    ```bash
    docker-compose up --build -d
    ```
    Este comando automatiza todo o processo: constrói a imagem do frontend, baixa as demais, cria a rede e inicia todos os serviços na ordem correta. Na primeira execução, o serviço `importer` popula o banco de dados com os dados iniciais. Esta operação ocorre apenas uma vez para não sobrescrever dados existentes.

### Onde Acessar

Após a inicialização, a aplicação estará disponível nos seguintes endereços:

* **Aplicação Web:** [http://localhost:8080](http://localhost:8080)
* **Conexão com o Banco (pgAdmin, etc.):**
    * **Host:** `localhost`
    * **Porta:** `5433`
    * **Usuário:** `postgres`
    * **Senha:** `postgres`
    * **Database:** `MovieFlix-db`

### Para Desligar a Aplicação

Para parar и remover todos os contêineres da aplicação, utilize o seguinte comando na pasta do projeto:
```bash
docker-compose down