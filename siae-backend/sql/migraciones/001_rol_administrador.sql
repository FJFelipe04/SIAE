-- Agrega el perfil 'administrador' a una base de datos SIAE ya creada (PostgreSQL).
-- Uso: psql -d siae -f sql/migraciones/001_rol_administrador.sql
-- Luego crear el primer administrador con:  python -m app.crear_admin
DO $$
DECLARE restriccion text;
BEGIN
    SELECT conname INTO restriccion FROM pg_constraint
    WHERE conrelid = 'usuario'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%perfil%';
    IF restriccion IS NOT NULL THEN
        EXECUTE format('ALTER TABLE usuario DROP CONSTRAINT %I', restriccion);
    END IF;
END $$;
ALTER TABLE usuario ADD CONSTRAINT usuario_perfil_check
    CHECK (perfil IN ('analista','jefe_comercial','administrador'));
