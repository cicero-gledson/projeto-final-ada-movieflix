FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY index.html /usr/share/nginx/html/index.html
COPY cadastrar-filme.html /usr/share/nginx/html/cadastrar-filme.html
COPY cadastrar-usuario.html /usr/share/nginx/html/cadastrar-usuario.html
COPY cadastrar-avaliacao.html /usr/share/nginx/html/cadastrar-avaliacao.html

EXPOSE 80
