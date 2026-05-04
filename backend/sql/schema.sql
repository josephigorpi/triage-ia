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
    nivel_urgencia VARCHAR(20),
    conducta_sugerida TEXT
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

-- Índices
CREATE INDEX idx_triajes_fecha ON triajes(fecha_hora);
CREATE INDEX idx_triajes_paciente ON triajes(id_paciente);
CREATE INDEX idx_triajes_nivel ON triajes(nivel_urgencia);
CREATE INDEX idx_logs_usuario ON logs_auditoria(id_usuario);
CREATE INDEX idx_logs_fecha ON logs_auditoria(fecha_hora);

-- Insertar usuario admin (contraseña: admin123)
-- Hash generado con: python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol) VALUES ('admin', '$2b$12$RqfVJm7YrXqXqXqXqXqXuO0x5x5x5x5x5x5x5x5x5x5x5x5', 'administrador');

-- Insertar algunos pacientes de ejemplo
INSERT INTO pacientes (nombre_completo, fecha_nacimiento, genero, contacto) VALUES
('Juan Pérez', '1985-03-15', 'Masculino', '555-1001'),
('María García', '1990-07-22', 'Femenino', '555-1002'),
('Carlos López', '1978-11-30', 'Masculino', '555-1003'),
('Ana Rodríguez', '2000-05-18', 'Femenino', '555-1004');

-- Insertar algunos triajes de ejemplo (con nivel_urgencia)
INSERT INTO triajes (id_paciente, id_usuario, presion_arterial_sist, presion_arterial_diast, frecuencia_cardiaca, temperatura, saturacion_oxigeno, sintomas, nivel_urgencia, conducta_sugerida) VALUES
(1, 1, 120, 80, 75, 36.5, 98, 'Dolor de cabeza leve', 'bajo', 'Reposo y control'),
(1, 1, 130, 85, 88, 37.2, 96, 'Fiebre y malestar', 'moderado', 'Evaluación médica'),
(2, 1, 110, 70, 72, 36.8, 99, 'Chequeo rutina', 'bajo', 'Sin complicaciones'),
(3, 1, 160, 95, 95, 37.5, 94, 'Dolor en el pecho', 'alto', 'Evaluación prioritaria');

-- Insertar resultados IA de ejemplo
INSERT INTO resultados_ia (id_triaje, nivel_urgencia_ia, conducta_sugerida_ia, diagnosticos_diferenciales) VALUES
(1, 'bajo', 'Reposo en casa', 'Cefalea tensional, Migraña'),
(2, 'moderado', 'Consulta médica en 24h', 'Infección viral, Deshidratación'),
(3, 'alto', 'Acudir a urgencias', 'Hipertensión, Problema cardíaco');

-- Insertar logs de auditoría de ejemplo
INSERT INTO logs_auditoria (id_usuario, accion, detalles) VALUES
(1, 'login', 'Inicio de sesión desde nueva máquina'),
(1, 'crear_triaje', 'Triaje ID 1 creado para paciente Juan Pérez'),
(1, 'crear_triaje', 'Triaje ID 2 creado para paciente Juan Pérez'),
(1, 'crear_triaje', 'Triaje ID 3 creado para paciente María García');