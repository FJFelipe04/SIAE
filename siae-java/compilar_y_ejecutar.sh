#!/bin/sh
# Compila y ejecuta el módulo. Requiere JDK 17 o superior.
set -e
mkdir -p out
javac -encoding UTF-8 -d out $(find src -name "*.java")
java -cp "out:lib/postgresql-42.7.4.jar" co.sena.siae.AplicacionUsuarios "$@"
