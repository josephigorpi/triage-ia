-- Crear base de datos (opcional, puede hacerse fuera)
CREATE DATABASE triaje_ia;
\c triaje_ia;

-- Tabla: usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'medico',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: pacientes
CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(200) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20),
    contacto VARCHAR(100),
    direccion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: triajes
CREATE TABLE triajes (
    id_triaje SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    presion_arterial_sist INTEGER,
    presion_arterial_diast INTEGER,
    frecuencia_cardiaca INTEGER,
    temperatura NUMERIC(4,1),
    saturacion_oxigeno INTEGER,
    sintomas TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nivel_urgencia VARCHAR(20),      -- bajo, moderado, alto, crítico
    conducta_sugerida TEXT,
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla: resultados_ia
CREATE TABLE resultados_ia (
    id_resultado SERIAL PRIMARY KEY,
    id_triaje INTEGER NOT NULL REFERENCES triajes(id_triaje) ON DELETE CASCADE,
    nivel_urgencia_ia VARCHAR(20),
    conducta_sugerida_ia TEXT,
    diagnosticos_diferenciales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: logs_auditoria
CREATE TABLE logs_auditoria (
    id_log SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_origen VARCHAR(45)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_triajes_fecha ON triajes(fecha_hora);
CREATE INDEX idx_triajes_paciente ON triajes(id_paciente);
CREATE INDEX idx_triajes_nivel ON triajes(nivel_urgencia);
CREATE INDEX idx_logs_usuario ON logs_auditoria(id_usuario);
CREATE INDEX idx_logs_fecha ON logs_auditoria(fecha_hora);

-- Insertar usuario admin por defecto (contraseña: admin123 - en producción cambiar)
-- La contraseña debe estar hasheada con bcrypt. Ejemplo con contraseña 'admin123':
-- Para obtener el hash, usar: python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol) VALUES ('admin', '$2b$12$5NpzJpM3nPm3jN3nPm3jN3nPm3jN3nPm3jN3nPm3jN3nPm3jN3nPm3jN3', 'administrador');