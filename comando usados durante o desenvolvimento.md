# criar a rede movieflix-network
docker network create movieflix-network

# criar o volume: 
docker volume create db_postgresql


# criar a imagem do postgres rodando na porta 5432 do contêiner e acessada na porta 5433 do localhost:
docker run --rm --name db-movieflix --network movieflix-network -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=MovieFlix-db -v db_postgresql:/var/lib/postgresql/data -p 5433:5432 -d postgres:14-alpine


# IMPORTAR. CRIAR imagem com o app que vai importar os dados dos arquivos csv para o db postgres. (Data Lake -> Data Warehouse)
docker build -t cicerogledson/app-data-lake-to-postgres:latest .
## enviado para o repositório Docker:
docker push cicerogledson/app-data-lake-to-postgres:latest


## IMPORTAR: comando para RODAR o contêiner que vai transformar os dados do Data Lake para o Data Warehouse:
docker build -t cicerogledson/app-data-lake-to-postgres:lates ./dados
docker run --rm --name app-movieflix-importer --network movieflix-network -e DATABASE_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" -v "$(pwd)/dados":/app/dados cicerogledson/app-data-lake-to-postgres:lates



# para CRIAR o conteiner com o app que vai devolver as consultas feitas ao db postgres
docker build -t cicerogledson/app-movieflix-backend-relatorios:latest .
## para RODAR o conteiner com o app que vai devolver as consultas feitas ao db postgres
docker run --rm --name app-movieflix-backend-relatorios --network movieflix-network -e DB_HOST=db-movieflix -e DB_PORT=5432 -d cicerogledson/app-movieflix-backend-relatorios:latest

# NOVO
docker run --rm --name app-movieflix-backend-relatorios --network movieflix-network -p 5000:5000 -e DATABASE_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" -d cicerogledson/movieflix-api:latest


# para criar a imagem nginx do proxy reverso que servirá index.html em www.movieflix.com 
docker build -t cicerogledson/movieflix-proxy-web:latest .
docker push cicerogledson/movieflix-proxy-web:latest
## para rodar o contêiner:
docker run --rm --name movieflix-proxy-web -p 8080:80 --network movieflix-network -d cicerogledson/movieflix-frontend:latest

Acesso por:
http://localhost:8080
ou,  criada uma entrada no arquivo C:\Windows\System32\drivers\etc\hosts com "127.0.0.1 www.movieflix.com", pode acessar  por:
http://www.movieflix.com:8080/

# -------------------------------------------------------------------------

# para subir tudo com o docker compose
docker-compose up --build -d

# para remover todos os contêiners
docker-compose down

# para parar apenas o frontend:
docker-compose stop frontend


# para iniciar novamente apenas o frontend:
docker-compose up -d frontend

# para reiniciar (parar e iniciar) apenas a API:
docker-compose restart api

# para reconstruir e reiniciar apenas o frontend após uma alteração no código:
docker-compose up -d --build frontend

# para reiniciar tudo
docker-compose restart

# para reconstruir as imagens e subir os contêiners:
docker-compose up --build -d