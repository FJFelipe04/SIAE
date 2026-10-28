#!/bin/sh
# Compila el servlet (y el DAO de ../siae-java) dentro de webapp/WEB-INF/classes.
# Uso: CATALINA_HOME=/ruta/a/apache-tomcat-10.1.x ./construir.sh   y luego copiar webapp/ a $CATALINA_HOME/webapps/siae-web
set -e
mkdir -p webapp/WEB-INF/classes webapp/WEB-INF/lib
javac -encoding UTF-8 -cp "$CATALINA_HOME/lib/servlet-api.jar" -d webapp/WEB-INF/classes $(find src ../siae-java/src -name "*.java")
cp ../siae-java/lib/postgresql-42.7.4.jar webapp/WEB-INF/lib/
echo "Listo: webapp/ es la aplicación desplegable"
