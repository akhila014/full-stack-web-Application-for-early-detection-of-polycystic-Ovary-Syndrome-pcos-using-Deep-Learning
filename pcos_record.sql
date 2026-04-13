

CREATE TABLE pcos_records (
    id SERIAL PRIMARY KEY,
    age INTEGER,
    symptoms TEXT,
    prediction VARCHAR(50),
    image_path VARCHAR(255)
);