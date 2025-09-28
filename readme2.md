# Projeto Final – MovieFlix Analytics - 27/09/2025

Plataforma simples de cadastro e avaliação de filmes. Também faz análises de dados gerados pelos usuários para entender preferências, tendências e apoiar decisões de negócio.

Para rodar a aplicação, siga os seguintes passos:

# 1 - criar a rede movieflix-network: 
docker network create movieflix-network

# 2 - criar o volume: 
docker volume create db_postgresql

# 3 - rodar um conteiner postgres rodando na porta 5432 do contêiner e acessado na porta 5433 do localhost:
docker run --rm --name db-movieflix --network movieflix-network -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=MovieFlix-db -v db_postgresql:/var/lib/postgresql/data -p 5433:5432 -d postgres:14-alpine


# 4 - importar dados do "Data Lake" para o "Data Warehouse" (tabelas postgres) 
rode um conteiner que vai pegar pegar os dados dos arquivos ./dados/filmes.csv, ./dados/usuarios.csv e .dados/avaliacoes.csv e imporrtá-los para o banco de dados relacional movieFlix-db. Os arquivos citados acima devem estar na pasta ./dados:

docker run --rm --name app-movieflix-importer --network movieflix-network -e DATABASE_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" -v "$(pwd)/dados":/app/dados cicerogledson/app-data-lake-to-postgres:lates

* Esse conteiner deve ser executado apenas uma vez, pois ele cria as tabelas no banco de dados e importa os dados dos arquivos. Se obanco já tiver dados, os dados serão apagados. 


# 5 - rodar o conteiner com o "backend" da applicação. É esse conteiner que vai acessar o DB e atender às requisições do frontend: 
docker run --rm --name app-movieflix-backend-relatorios --network movieflix-network -p 5000:5000 -e DATABASE_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" -d cicerogledson/app-movieflix-backend-relatorios:latest


# 6 - rodar o conteiner com o frontend e o proxy reverso:
docker run --rm --name movieflix-proxy-web -p 8080:80 --network movieflix-network -d cicerogledson/movieflix-proxy-web:latest

Acesso por:
http://localhost:8080
