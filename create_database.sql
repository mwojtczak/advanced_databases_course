-- RELATION DATABASE - POSTGRES

DROP TABLE IF EXISTS publication_author;
DROP TABLE IF EXISTS publication_cite;
DROP TABLE IF EXISTS url;
DROP TABLE IF EXISTS ee;
DROP TABLE IF EXISTS publication;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS publisher;
DROP TABLE IF EXISTS editor;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS title;
DROP TYPE IF EXISTS publication_type;

CREATE TYPE publication_type AS ENUM ('article', 'inproceedings', 'proceedings', 'book', 'incollection',
'phdthesis', 'mastersthesis', 'www');


CREATE TABLE series(
	id SERIAL PRIMARY KEY,
	name VARCHAR(300),
	href VARCHAR(350)
);

CREATE TABLE note(
	id SERIAL PRIMARY KEY,
	label VARCHAR(300),
	type VARCHAR(150)
);

CREATE TABLE publisher(
	id SERIAL PRIMARY KEY,
	publisher VARCHAR(500),
	href VARCHAR(350)
);

CREATE TABLE editor(
	id SERIAL PRIMARY KEY,
	editor VARCHAR(350),
	aux VARCHAR(350),
	orcid VARCHAR(350)
);

CREATE TABLE author(
	id SERIAL PRIMARY KEY,
	aux VARCHAR(150),
	bibtex VARCHAR(150),
	orcid VARCHAR(350),
	name VARCHAR(350)
);

CREATE TABLE title(
	id SERIAL PRIMARY KEY,
	title VARCHAR(2000),
	bibtex VARCHAR(300)
);

CREATE TABLE publication(
	key VARCHAR(100) PRIMARY KEY,
	type publication_type,
	booktitle VARCHAR(150),
	publtype VARCHAR(300),
	mdate date,
	title INTEGER REFERENCES title(id),
	volume VARCHAR(100),
	year INTEGER,
	journal VARCHAR(150),
	month VARCHAR(50),
	publisher INTEGER REFERENCES publisher(id),
	editor INTEGER REFERENCES editor(id),
	school VARCHAR(200),
	note INTEGER REFERENCES note(id),
	isbn VARCHAR(150),
	chapter VARCHAR(50),
	series INTEGER REFERENCES series(id),
	cdrom VARCHAR(100),
	crossref VARCHAR(400),
	number VARCHAR(20),
	pages VARCHAR(20)
);

CREATE TABLE publication_author(
	id SERIAL PRIMARY KEY,
	publication VARCHAR(100),
	-- REFERENCES publication(key),
	author INTEGER REFERENCES author(id)
);

CREATE TABLE publication_cite(
	id SERIAL PRIMARY KEY,
	publication VARCHAR(100),
	-- REFERENCES publication(key),
	label VARCHAR(300),
	ref VARCHAR(250)
);

CREATE TABLE url(
	id SERIAL PRIMARY KEY,
	url VARCHAR(350),
	aux VARCHAR(250),
	publication VARCHAR(100)
	-- REFERENCES publication(key)
);

CREATE TABLE ee(
	id SERIAL PRIMARY KEY,
	ee VARCHAR(700),
	aux VARCHAR(350),
	publication VARCHAR(100)
	-- REFERENCES publication(key)
);
