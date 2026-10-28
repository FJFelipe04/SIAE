#!/usr/bin/env bash
# Configura Apache + PHP + MySQL en una máquina virtual Ubuntu (GA10-AA5, virtualización).
# Uso dentro de la VM:  sudo bash instalar_ubuntu.sh
set -euo pipefail
CLAVE_BD="${CLAVE_BD:-siae_local}"
apt-get update
apt-get install -y apache2 mysql-server php libapache2-mod-php php-mysql curl
systemctl enable --now apache2 mysql
mysql <<SQL
CREATE DATABASE IF NOT EXISTS siae CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'siae'@'localhost' IDENTIFIED BY '${CLAVE_BD}';
GRANT ALL PRIVILEGES ON siae.* TO 'siae'@'localhost';
FLUSH PRIVILEGES;
SQL
if [ -f siae_mysql.sql ]; then mysql siae < siae_mysql.sql; fi
cp index.php /var/www/html/index.php && rm -f /var/www/html/index.html
cat > /etc/apache2/conf-available/siae-env.conf <<CONF
SetEnv DB_HOST localhost
SetEnv DB_NAME siae
SetEnv DB_USER siae
SetEnv DB_PASSWORD ${CLAVE_BD}
CONF
a2enconf siae-env && systemctl reload apache2
ufw allow 'Apache' || true
echo "--- Verificación ---"
systemctl is-active apache2 mysql
curl -s http://localhost/ | grep -o '<li>.*</li>'
