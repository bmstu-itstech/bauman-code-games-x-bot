CREATE TABLE ref_sources (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

ALTER TABLE participants ADD COLUMN ref_code TEXT REFERENCES ref_sources(code);