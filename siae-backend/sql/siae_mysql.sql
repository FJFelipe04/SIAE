CREATE DATABASE IF NOT EXISTS siae CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE siae;

-- Empresa (PYME) que usa el sistema.
CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador de la empresa',
    nombre VARCHAR(120) NOT NULL COMMENT 'Razón social',
    nit VARCHAR(20) NOT NULL UNIQUE COMMENT 'NIT de la empresa',
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de registro'
) ENGINE=InnoDB COMMENT='Empresa (PYME) que usa el sistema.';

-- Analista o jefe comercial que usa SIAE.
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador del usuario',
    empresa_id INTEGER NOT NULL COMMENT 'Empresa a la que pertenece',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo',
    correo VARCHAR(150) NOT NULL UNIQUE COMMENT 'Correo de inicio de sesión',
    contrasena_hash VARCHAR(255) NOT NULL COMMENT 'Contraseña protegida con bcrypt (nunca en texto plano)',
    perfil VARCHAR(20) NOT NULL DEFAULT 'analista' CHECK (perfil IN ('analista','jefe_comercial')) COMMENT 'Perfil del usuario',
    activo BOOLEAN NOT NULL DEFAULT true COMMENT 'Si la cuenta está habilitada',
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de registro',
    ultimo_acceso DATETIME NULL COMMENT 'Último inicio de sesión',
    CONSTRAINT fk_usuario_empresa_id FOREIGN KEY (empresa_id) REFERENCES empresa(id)
) ENGINE=InnoDB COMMENT='Analista o jefe comercial que usa SIAE.';

-- Archivo .xlsx o .csv cargado. Nunca se modifica.
CREATE TABLE archivo_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador del archivo',
    usuario_id INTEGER NOT NULL COMMENT 'Usuario que lo cargó',
    nombre_original VARCHAR(255) NOT NULL COMMENT 'Nombre del archivo',
    formato VARCHAR(4) NOT NULL CHECK (formato IN ('xlsx','csv')) COMMENT 'Formato del archivo',
    tamano_bytes BIGINT NOT NULL CHECK (tamano_bytes <= 52428800) COMMENT 'Tamaño (máximo 50 MB)',
    cantidad_registros INTEGER NOT NULL CHECK (cantidad_registros <= 500000) COMMENT 'Filas del archivo (máximo 500.000)',
    ruta_almacenamiento VARCHAR(500) NOT NULL COMMENT 'Ubicación del archivo original en el servidor',
    hash_sha256 CHAR(64) NOT NULL COMMENT 'Huella para comprobar que el original no cambió',
    cargado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de carga',
    CONSTRAINT fk_archivo_ventas_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB COMMENT='Archivo .xlsx o .csv cargado. Nunca se modifica.';

-- Columnas detectadas en un archivo.
CREATE TABLE columna_archivo (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    archivo_id INTEGER NOT NULL COMMENT 'Archivo al que pertenece',
    nombre_original VARCHAR(150) NOT NULL COMMENT 'Encabezado original',
    posicion SMALLINT NOT NULL COMMENT 'Posición de la columna (desde 1)',
    tipo_detectado VARCHAR(10) NOT NULL CHECK (tipo_detectado IN ('texto','numero','fecha')) COMMENT 'Tipo inferido',
    CONSTRAINT fk_columna_archivo_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Columnas detectadas en un archivo.';

-- Indica qué columna es la fecha y cuál el valor de venta.
CREATE TABLE mapeo_campos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    archivo_id INTEGER NOT NULL UNIQUE COMMENT 'Archivo mapeado (uno por archivo)',
    columna_fecha_id INTEGER NOT NULL COMMENT 'Columna que contiene la fecha',
    columna_valor_id INTEGER NOT NULL COMMENT 'Columna que contiene el valor de venta',
    CONSTRAINT fk_mapeo_campos_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id),
    CONSTRAINT fk_mapeo_campos_columna_fecha_id FOREIGN KEY (columna_fecha_id) REFERENCES columna_archivo(id),
    CONSTRAINT fk_mapeo_campos_columna_valor_id FOREIGN KEY (columna_valor_id) REFERENCES columna_archivo(id)
) ENGINE=InnoDB COMMENT='Indica qué columna es la fecha y cuál el valor de venta.';

-- Trabajo temporal sobre un archivo antes de confirmar.
CREATE TABLE sesion_transformacion (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    archivo_id INTEGER NOT NULL COMMENT 'Archivo que se transforma',
    usuario_id INTEGER NOT NULL COMMENT 'Usuario que transforma',
    estado VARCHAR(12) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','confirmada','cancelada')) COMMENT 'Estado de la sesión',
    iniciada_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Inicio',
    cerrada_en DATETIME NULL COMMENT 'Fecha de confirmación o cancelación',
    CONSTRAINT fk_sesion_transformacion_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id),
    CONSTRAINT fk_sesion_transformacion_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB COMMENT='Trabajo temporal sobre un archivo antes de confirmar.';

-- Cada transformación aplicada, en orden.
CREATE TABLE paso_transformacion (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    sesion_id INTEGER NOT NULL COMMENT 'Sesión a la que pertenece',
    orden SMALLINT NOT NULL COMMENT 'Orden de aplicación (único por sesión)',
    tipo VARCHAR(25) NOT NULL CHECK (tipo IN ('eliminar_columna','renombrar_columna','cambiar_tipo','formato_fecha','quitar_duplicados','quitar_caracteres')) COMMENT 'Tipo de transformación',
    columna_objetivo VARCHAR(150) NULL COMMENT 'Columna afectada (NULL si aplica a todas)',
    parametros JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Parámetros (nuevo nombre, formato, caracteres)',
    aplicado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de aplicación',
    UNIQUE (sesion_id, orden),
    CONSTRAINT fk_paso_transformacion_sesion_id FOREIGN KEY (sesion_id) REFERENCES sesion_transformacion(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Cada transformación aplicada, en orden.';

-- Resultado guardado al confirmar.
CREATE TABLE tabla_transformada (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    sesion_id INTEGER NOT NULL UNIQUE COMMENT 'Sesión que la generó',
    usuario_id INTEGER NOT NULL COMMENT 'Dueño de la tabla',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre dado por el usuario (único por usuario)',
    filas INTEGER NOT NULL COMMENT 'Número de filas',
    columnas SMALLINT NOT NULL COMMENT 'Número de columnas',
    creada_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    UNIQUE (usuario_id, nombre),
    CONSTRAINT fk_tabla_transformada_sesion_id FOREIGN KEY (sesion_id) REFERENCES sesion_transformacion(id),
    CONSTRAINT fk_tabla_transformada_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB COMMENT='Resultado guardado al confirmar.';

-- Cada fila de una tabla transformada.
CREATE TABLE registro_venta (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    tabla_id INTEGER NOT NULL COMMENT 'Tabla a la que pertenece',
    fecha DATE NOT NULL COMMENT 'Fecha de la venta (columna mapeada)',
    valor NUMERIC(14,2) NOT NULL COMMENT 'Valor de la venta (columna mapeada)',
    datos JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Demás columnas de la fila',
    CONSTRAINT fk_registro_venta_tabla_id FOREIGN KEY (tabla_id) REFERENCES tabla_transformada(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Cada fila de una tabla transformada.';

-- Reporte generado sobre una tabla transformada.
CREATE TABLE reporte (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    tabla_id INTEGER NOT NULL COMMENT 'Tabla analizada',
    usuario_id INTEGER NOT NULL COMMENT 'Quién lo generó',
    tipo VARCHAR(15) NOT NULL CHECK (tipo IN ('tabla_dinamica','barras','lineas','torta')) COMMENT 'Tipo de reporte',
    fecha_inicio DATE NULL COMMENT 'Inicio del filtro',
    fecha_fin DATE NULL COMMENT 'Fin del filtro (no puede ser menor que fecha_inicio)',
    agrupacion VARCHAR(10) NOT NULL DEFAULT 'mes' CHECK (agrupacion IN ('dia','mes','anio')) COMMENT 'Agrupación',
    generado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de generación',
    CONSTRAINT ck_reporte_rango CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT fk_reporte_tabla_id FOREIGN KEY (tabla_id) REFERENCES tabla_transformada(id),
    CONSTRAINT fk_reporte_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB COMMENT='Reporte generado sobre una tabla transformada.';

-- Indicadores calculados en un reporte.
CREATE TABLE indicador (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    reporte_id INTEGER NOT NULL COMMENT 'Reporte al que pertenece',
    nombre VARCHAR(60) NOT NULL COMMENT 'Ej. ventas totales, crecimiento',
    valor NUMERIC(16,4) NOT NULL COMMENT 'Resultado',
    formula VARCHAR(200) NOT NULL COMMENT 'Fórmula usada',
    CONSTRAINT fk_indicador_reporte_id FOREIGN KEY (reporte_id) REFERENCES reporte(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Indicadores calculados en un reporte.';

-- Registro de acciones para seguridad.
CREATE TABLE bitacora_auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador',
    usuario_id INTEGER NULL COMMENT 'Usuario (NULL si el acceso falló)',
    accion VARCHAR(40) NOT NULL COMMENT 'Ej. login_ok, login_fallido, carga, confirmacion',
    detalle TEXT NULL COMMENT 'Información adicional',
    ip VARCHAR(45) NULL COMMENT 'Dirección IP',
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de la acción',
    CONSTRAINT fk_bitacora_auditoria_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB COMMENT='Registro de acciones para seguridad.';
