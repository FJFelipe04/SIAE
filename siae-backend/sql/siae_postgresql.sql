-- Empresa (PYME) que usa el sistema.
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    nit VARCHAR(20) NOT NULL UNIQUE,
    creado_en TIMESTAMP NOT NULL DEFAULT now()
);

-- Analista, jefe comercial o administrador (control global) que usa SIAE.
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(20) NOT NULL DEFAULT 'analista' CHECK (perfil IN ('analista','jefe_comercial','administrador')),
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_en TIMESTAMP NOT NULL DEFAULT now(),
    ultimo_acceso TIMESTAMP,
    CONSTRAINT fk_usuario_empresa_id FOREIGN KEY (empresa_id) REFERENCES empresa(id)
);

-- Archivo .xlsx o .csv cargado. Nunca se modifica.
CREATE TABLE archivo_ventas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    formato VARCHAR(4) NOT NULL CHECK (formato IN ('xlsx','csv')),
    tamano_bytes BIGINT NOT NULL CHECK (tamano_bytes <= 52428800),
    cantidad_registros INTEGER NOT NULL CHECK (cantidad_registros <= 500000),
    ruta_almacenamiento VARCHAR(500) NOT NULL,
    hash_sha256 CHAR(64) NOT NULL,
    cargado_en TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_archivo_ventas_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Columnas detectadas en un archivo.
CREATE TABLE columna_archivo (
    id SERIAL PRIMARY KEY,
    archivo_id INTEGER NOT NULL,
    nombre_original VARCHAR(150) NOT NULL,
    posicion SMALLINT NOT NULL,
    tipo_detectado VARCHAR(10) NOT NULL CHECK (tipo_detectado IN ('texto','numero','fecha')),
    CONSTRAINT fk_columna_archivo_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id) ON DELETE CASCADE
);

-- Indica qué columna es la fecha y cuál el valor de venta.
CREATE TABLE mapeo_campos (
    id SERIAL PRIMARY KEY,
    archivo_id INTEGER NOT NULL UNIQUE,
    columna_fecha_id INTEGER NOT NULL,
    columna_valor_id INTEGER NOT NULL,
    CONSTRAINT fk_mapeo_campos_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id),
    CONSTRAINT fk_mapeo_campos_columna_fecha_id FOREIGN KEY (columna_fecha_id) REFERENCES columna_archivo(id),
    CONSTRAINT fk_mapeo_campos_columna_valor_id FOREIGN KEY (columna_valor_id) REFERENCES columna_archivo(id)
);

-- Trabajo temporal sobre un archivo antes de confirmar.
CREATE TABLE sesion_transformacion (
    id SERIAL PRIMARY KEY,
    archivo_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    estado VARCHAR(12) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','confirmada','cancelada')),
    iniciada_en TIMESTAMP NOT NULL DEFAULT now(),
    cerrada_en TIMESTAMP,
    CONSTRAINT fk_sesion_transformacion_archivo_id FOREIGN KEY (archivo_id) REFERENCES archivo_ventas(id),
    CONSTRAINT fk_sesion_transformacion_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Cada transformación aplicada, en orden.
CREATE TABLE paso_transformacion (
    id SERIAL PRIMARY KEY,
    sesion_id INTEGER NOT NULL,
    orden SMALLINT NOT NULL,
    tipo VARCHAR(25) NOT NULL CHECK (tipo IN ('eliminar_columna','renombrar_columna','cambiar_tipo','formato_fecha','quitar_duplicados','quitar_caracteres')),
    columna_objetivo VARCHAR(150),
    parametros JSONB NOT NULL DEFAULT '{}',
    aplicado_en TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (sesion_id, orden),
    CONSTRAINT fk_paso_transformacion_sesion_id FOREIGN KEY (sesion_id) REFERENCES sesion_transformacion(id) ON DELETE CASCADE
);

-- Resultado guardado al confirmar.
CREATE TABLE tabla_transformada (
    id SERIAL PRIMARY KEY,
    sesion_id INTEGER NOT NULL UNIQUE,
    usuario_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    filas INTEGER NOT NULL,
    columnas SMALLINT NOT NULL,
    creada_en TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (usuario_id, nombre),
    CONSTRAINT fk_tabla_transformada_sesion_id FOREIGN KEY (sesion_id) REFERENCES sesion_transformacion(id),
    CONSTRAINT fk_tabla_transformada_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Cada fila de una tabla transformada.
CREATE TABLE registro_venta (
    id BIGSERIAL PRIMARY KEY,
    tabla_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    valor NUMERIC(14,2) NOT NULL,
    datos JSONB NOT NULL DEFAULT '{}',
    CONSTRAINT fk_registro_venta_tabla_id FOREIGN KEY (tabla_id) REFERENCES tabla_transformada(id) ON DELETE CASCADE
);

-- Reporte generado sobre una tabla transformada.
CREATE TABLE reporte (
    id SERIAL PRIMARY KEY,
    tabla_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    tipo VARCHAR(15) NOT NULL CHECK (tipo IN ('tabla_dinamica','barras','lineas','torta')),
    fecha_inicio DATE,
    fecha_fin DATE,
    agrupacion VARCHAR(10) NOT NULL DEFAULT 'mes' CHECK (agrupacion IN ('dia','mes','anio')),
    generado_en TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_reporte_rango CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT fk_reporte_tabla_id FOREIGN KEY (tabla_id) REFERENCES tabla_transformada(id),
    CONSTRAINT fk_reporte_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Indicadores calculados en un reporte.
CREATE TABLE indicador (
    id SERIAL PRIMARY KEY,
    reporte_id INTEGER NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    valor NUMERIC(16,4) NOT NULL,
    formula VARCHAR(200) NOT NULL,
    CONSTRAINT fk_indicador_reporte_id FOREIGN KEY (reporte_id) REFERENCES reporte(id) ON DELETE CASCADE
);

-- Registro de acciones para seguridad.
CREATE TABLE bitacora_auditoria (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INTEGER,
    accion VARCHAR(40) NOT NULL,
    detalle TEXT,
    ip VARCHAR(45),
    fecha TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_bitacora_auditoria_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);
