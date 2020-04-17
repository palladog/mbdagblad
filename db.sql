\set ON_ERROR_STOP on

\c ah9829

-- Drop, create, and move to database
DROP DATABASE IF EXISTS mdagblad;
CREATE DATABASE mdagblad;
REVOKE ALL PRIVILEGES ON DATABASE mbdagblad FROM public;
\c mbdagblad

-- Tables 
CREATE TABLE article (
    id SERIAL NOT NULL,
    headline VARCHAR(100) NOT NULL,
    preamble TEXT NOT NULL,
    body TEXT NOT NULL,
    published TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0), 
    PRIMARY KEY (id)
);

CREATE TABLE journalist (
    id SERIAL NOT NULL,
    pnr CHAR(12) NOT NULL,
    name VARCHAR(50) NOT NULL,
    note TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE written_by (
    journalist_id SERIAL NOT NULL,
    article_id SERIAL NOT NULL,
    FOREIGN KEY (journalist_id) REFERENCES journalist(id),
    FOREIGN KEY (article_id) REFERENCES article(id),
    PRIMARY KEY (journalist_id, article_id)
);

CREATE TABLE image (
    id SERIAL NOT NULL,
    url TEXT NOT NULL,
    alt_text TEXT NOT NULL,
    published TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    PRIMARY KEY (id)
);

CREATE TABLE article_image (
    image_id SERIAL NOT NULL,
    article_id SERIAL NOT NULL,
    caption TEXT,
    FOREIGN KEY (image_id) REFERENCES image(id),
    FOREIGN KEY (article_id) REFERENCES article(id),
    PRIMARY KEY (image_id, article_id)
);

CREATE TABLE comment (
    id SERIAL NOT NULL,
    article_id SERIAL NOT NULL,
    signature VARCHAR(50) NOT NULL,
    published TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0), 
    text TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES article(id),
    PRIMARY KEY (id)
);

-- Inserts
INSERT INTO article (headline, preamble, body) VALUES ('Här är böckerna du inte bör missa', 'Vi guidar till den mest intressanta litteraturen vecka 16.', 'Självbiografisk eller ej är Jackie klart och tydligt en roman, en berättelse noggrant bearbetad och utmejslad med fiktionens verktyg. Swärd är skicklig på att hitta de där avgörande scenerna och ögonblicken som finns i alla liv, men som inte träder fram i full klarhet, ens för oss själva, förrän vi bearbetat dem i minnet så många varv att de till slut antagit fiktionens form, blivit ett slags livsberättelse som går att leva med, kanske till och med förstå.');
INSERT INTO journalist (pnr, name, note) VALUES ('199001015667', 'Hans Hansson', 'Fotboll, godis och bajs'), ('198902024545', 'Stig Stigsson', 'Musik och TV');
INSERT INTO written_by (journalist_id, article_id) VALUES (1, 1), (2, 1);
INSERT INTO image (url, alt_text) VALUES ('https://images.hdsydsvenskan.se/preset:large/1280x768/mf9pHOL7l8zikdj7RV5cbsNlSUc.jpg', 'Boken Jackie av Jennie Swärd');
INSERT INTO article_image (image_id, article_id, caption) VALUES (1, 1, 'Anne Swärd.');
INSERT INTO comment (article_id, signature, text) VALUES (1, 'Gukka', 'Bra artikel!.');