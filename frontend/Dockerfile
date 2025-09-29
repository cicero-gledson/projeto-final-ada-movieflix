# Usa um argumento para decidir qual arquivo de configuração usar
ARG NGINX_CONF_FILE=nginx.conf

FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf

# Copia o arquivo de configuração escolhido pelo argumento
COPY ${NGINX_CONF_FILE} /etc/nginx/conf.d/default.conf

# Copia os arquivos HTML
COPY index.html /usr/share/nginx/html/
COPY cadastrar-filme.html /usr/share/nginx/html/
COPY cadastrar-usuario.html /usr/share/nginx/html/
COPY cadastrar-avaliacao.html /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]