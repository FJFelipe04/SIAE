<?php
// Página de prueba: confirma que Apache, PHP y MySQL funcionan juntos.
$host = getenv('DB_HOST') ?: 'localhost';
try {
    $bd = new PDO("mysql:host=$host;dbname=" . (getenv('DB_NAME') ?: 'siae'), getenv('DB_USER') ?: 'siae', getenv('DB_PASSWORD') ?: '');
    $version = $bd->query('SELECT VERSION()')->fetchColumn();
    $tablas = $bd->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
    $estado = "Conectado a MySQL $version – " . count($tablas) . " tablas";
} catch (PDOException $e) {
    $estado = 'Error de conexión: ' . htmlspecialchars($e->getMessage());
}
?>
<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>SIAE – prueba de servicios</title></head>
<body style="font-family:Arial;margin:40px">
<h1>SIAE – prueba de servicios</h1>
<ul>
  <li>Servidor web: <?= htmlspecialchars($_SERVER['SERVER_SOFTWARE']) ?></li>
  <li>PHP: <?= PHP_VERSION ?></li>
  <li>Base de datos: <?= $estado ?></li>
</ul>
</body></html>
