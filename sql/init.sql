CREATE DATABASE TP_meds;

-- 1. Medicines Table
CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_medicines_name ON medicines(name);

-- 2. Symptoms Table
CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    severity_scale INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_symptoms_name ON symptoms(name);

-- 3. Medicine Effects (Many-to-Many Relationship)
CREATE TABLE medicine_effects (
    id SERIAL PRIMARY KEY,
    medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    symptom_id INTEGER NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
    effectiveness INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_medicine_symptom UNIQUE(medicine_id, symptom_id)
);

CREATE INDEX idx_medicine_effects_medicine_id ON medicine_effects(medicine_id);
CREATE INDEX idx_medicine_effects_symptom_id ON medicine_effects(symptom_id);

-- 4. Patients Table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patients_name ON patients(full_name);
CREATE INDEX idx_patients_email ON patients(email);

-- 5. Patient Symptoms (Link between Patients and Symptoms)
CREATE TABLE patient_symptoms (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    symptom_id INTEGER NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
    current_severity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_patient_symptom UNIQUE(patient_id, symptom_id)
);

CREATE INDEX idx_patient_symptoms_patient_id ON patient_symptoms(patient_id);
CREATE INDEX idx_patient_symptoms_symptom_id ON patient_symptoms(symptom_id);