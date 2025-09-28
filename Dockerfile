FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/

COPY index.html /usr/share/nginx/html/
COPY cadastrar-filme.html /usr/share/nginx/html/
COPY cadastrar-usuario.html /usr/share/nginx/html/
COPY cadastrar-avaliacao.html /usr/share/nginx/html/
EXPOSE 80
