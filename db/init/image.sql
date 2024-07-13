-- images.sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL
);

-- annotations.sql
CREATE TABLE annotations (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES images(id) ON DELETE CASCADE,
    class_label TEXT NOT NULL,
    x_center FLOAT NOT NULL,
    y_center FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL
);