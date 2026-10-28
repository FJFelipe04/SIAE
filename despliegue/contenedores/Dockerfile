# Servidor Apache sobre Ubuntu para la evidencia GA10-AA5 (contenedores)
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends apache2 php libapache2-mod-php php-mysql curl \
    && rm -rf /var/lib/apt/lists/* /var/www/html/index.html
COPY web/ /var/www/html/
EXPOSE 80
HEALTHCHECK CMD curl -fs http://localhost/ || exit 1
CMD ["apachectl", "-D", "FOREGROUND"]
