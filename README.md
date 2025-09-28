# **Projeto Final – MovieFlix Analytics**

## **Descrição**

Plataforma de cadastro e avaliação de filmes. O sistema coleta dados para análises de preferências e tendências de consumo.

## 

## **Como Executar**

Siga os passos abaixo no terminal para rodar a aplicação completa.

### **Passos**

1\. Crie a rede Docker  
Esta rede permite que os contêineres se comuniquem.  
docker network create movieflix-network

2\. Crie o volume do banco de dados  
Isso garante que os dados do banco não sejam perdidos.  
docker volume create db\_postgresql

**3\. Rode o contêiner do Banco de Dados**  
docker run \--rm \--name db-movieflix \--network movieflix-network \-e POSTGRES\_USER=postgres \-e POSTGRES\_PASSWORD=postgres \-e POSTGRES\_DB=MovieFlix-db \-v db\_postgresql:/var/lib/postgresql/data \-p 5433:5432 \-d postgres:14-alpine

4\. Importe os Dados  
Este contêiner cria as tabelas e importa os dados dos arquivos .csv.  
**Nota:** Este comando espera que os arquivos filmes.csv, usuarios.csv e avaliacoes.csv estejam localizados dentro de uma pasta chamada dados na raiz do projeto.  
docker run \--rm \--name app-movieflix-importer \--network movieflix-network \-e DATABASE\_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" \-v "$(pwd)/dados":/app/dados cicerogledson/movieflix-importer:latest

**5\. Rode o Backend (API)**  
docker run \--rm \--name app-movieflix-backend-relatorios \--network movieflix-network \-p 5000:5000 \-e DATABASE\_URL="postgresql://postgres:postgres@db-movieflix:5432/MovieFlix-db" \-d cicerogledson/movieflix-api:latest

**6\. Rode o Frontend**  
docker run \--rm \--name movieflix-proxy-web \-p 8080:80 \--network movieflix-network \-d cicerogledson/movieflix-frontend:latest

### **Acesso**

Após executar todos os passos, a aplicação estará disponível no seu navegador em:  
http://localhost:8080