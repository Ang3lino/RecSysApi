
-- Modificacion para coincidencia con el csv
ALTER TABLE producto MODIFY idProducto VARCHAR(20);
ALTER TABLE producto MODIFY nombre VARCHAR(400);
ALTER TABLE producto MODIFY marca VARCHAR(100);

ALTER TABLE producto ADD COLUMN img VARCHAR(200);

-- Modificacion de la llave primaria
SHOW CREATE TABLE sociomembresia;
ALTER TABLE sociomembresia DROP FOREIGN KEY sociomembresia_ibfk_1;
ALTER TABLE socio modify idSocio VARCHAR(40);
ALTER TABLE sociomembresia modify idSocio VARCHAR(40);
ALTER TABLE sociomembresia 
    ADD CONSTRAINT sociomembresia_ibfk_1 
    FOREIGN KEY (idSocio) REFERENCES socio (idSocio) 
    ON DELETE CASCADE ON UPDATE CASCADE;

-- Modificacion para coincidencia con el csv
ALTER TABLE socio MODIFY idSocio VARCHAR(40);
ALTER TABLE socio MODIFY nombre VARCHAR(120);

-- 
ALTER TABLE socio MODIFY genero ENUM('M', 'F');
ALTER TABLE socio ADD COLUMN fecha_nac DATE DEFAULT "1998-08-24";

-- Creacion de la relacion de ratings
DROP TABLE IF EXISTS valoracion;
CREATE TABLE valoracion (
    idSocio VARCHAR(40) COLLATE latin1_swedish_ci NOT NULL,
    idProducto VARCHAR(20) COLLATE latin1_swedish_ci NOT NULL,
    rating DOUBLE,
    unix_time VARCHAR(20),
    PRIMARY KEY(idSocio, idProducto)
);

ALTER TABLE valoracion 
    ADD CONSTRAINT valoracion_socio
    FOREIGN KEY (idSocio) REFERENCES socio(idSocio) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    
ALTER TABLE valoracion 
    ADD CONSTRAINT valoracion_producto
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto) 
        ON DELETE CASCADE ON UPDATE CASCADE; 

-- Campos agregados para socio. Como regla cada usuario tiene un unico email
ALTER TABLE socio ADD passwd VARCHAR(70) DEFAULT 'pass';
UPDATE socio SET email = CONCAT(idSocio, "@gmail.com");
ALTER TABLE socio ADD CONSTRAINT c_uniq_email_passwd  UNIQUE (email);


-- Creacion de la relacion de historial de compra
DROP TABLE IF EXISTS historial;
CREATE TABLE historial (
    idSocio VARCHAR(40) COLLATE latin1_swedish_ci NOT NULL,
    idProducto VARCHAR(20) COLLATE latin1_swedish_ci NOT NULL,
    fecha_hora DATETIME DEFAULT NOW() NOT NULL,
    cantidad INT DEFAULT 1,
    PRIMARY KEY (idSocio, idProducto, fecha_hora),
    FOREIGN KEY (idSocio) REFERENCES socio(idSocio) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- INSERT INTO historial (
--     idSocio ,
--     idProducto 
-- ) SELECT "1", idProducto FROM producto LIMIT 5 ; 
-- INSERT INTO historial (
--     idSocio ,
--     idProducto 
-- ) SELECT "2", idProducto FROM producto LIMIT 5 ; 
-- SELECT * FROM historial;
-- SELECT count(*) FROM historial GROUP BY fecha_hora;
-- DELETE FROM historial;


DROP TABLE IF EXISTS pendiente;
CREATE TABLE pendiente (
    idSocio VARCHAR(40) COLLATE latin1_swedish_ci NOT NULL,
    idProducto VARCHAR(20) COLLATE latin1_swedish_ci NOT NULL,
    PRIMARY KEY (idSocio, idProducto),
    FOREIGN KEY (idSocio) REFERENCES socio(idSocio) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- INSERT INTO pendiente(
--     idSocio ,
--     idProducto 
-- ) SELECT "1", idProducto FROM producto LIMIT 5 ; 
-- SELECT * FROM pendiente;
-- DELETE FROM pendiente;

SELECT MAX(idSubCat) FROM subcategoria;
INSERT INTO subcategoria(nombre, idCat, idSubCat) 
    VALUES 
        ('Comestibles y comida gourmet', 35, 459);

CREATE TABLE img_prod (
    idProducto VARCHAR(20) COLLATE latin1_swedish_ci,
    img_url VARCHAR(200),
    PRIMARY KEY (idProducto, img_url),
    FOREIGN KEY (idProducto) REFERENCES producto(idProducto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

UPDATE socio SET passwd = sha2('pass', 256);

ALTER TABLE sucursal ADD COLUMN coordenada POINT;


-- UPDATE sucursal SET coordenada = POINT(21.917009371685957, -102.287656148313463) WHERE idSuc = 1;
-- UPDATE sucursal SET coordenada = POINT(19.55124689171415, -99.2027616745069) WHERE idSuc = 2;
-- UPDATE sucursal SET coordenada = POINT(19.548301903668577, -99.27111304722405) WHERE idSuc = 3;
-- UPDATE sucursal SET coordenada = POINT(21.14350605824367, -86.8218038842816) WHERE idSuc = 4;
-- UPDATE sucursal SET coordenada = POINT(31.702796972522837, -106.4229265557612) WHERE idSuc = 5;

-- UPDATE sucursal SET coordenada = POINT(20.54544238262158, -100.82022930332225) WHERE idSuc = 6;
-- UPDATE sucursal SET coordenada = POINT(19.85676055096793, -99.28268549595845) WHERE idSuc = 7;
-- UPDATE sucursal SET coordenada = POINT(28.64899475081608, -106.13044430740158) WHERE idSuc = 8;
-- UPDATE sucursal SET coordenada = POINT(19.284400497242594, -99.13830756897899) WHERE idSuc = 9;

-- UPDATE sucursal SET coordenada = POINT(24.79911911056095, -107.42498457272889) WHERE idSuc = 11;
-- UPDATE sucursal SET coordenada = POINT(31.818057312991144, -116.59664183430024) WHERE idSuc = 12;
-- UPDATE sucursal SET coordenada = POINT(20.5784216828521, -103.44933013215645) WHERE idSuc = 13;
-- UPDATE sucursal SET coordenada = POINT(20.67930448865095, -103.42833994749405) WHERE idSuc = 14;
-- UPDATE sucursal SET coordenada = POINT(29.082927900160502, -110.97894337486588) WHERE idSuc = 15;

-- CDMX, EdoMex
UPDATE sucursal SET coordenada = POINT(19.55124689171415, -99.2027616745069) WHERE idSuc = 2;
UPDATE sucursal SET coordenada = POINT(19.548301903668577, -99.27111304722405) WHERE idSuc = 3;
UPDATE sucursal SET coordenada = POINT(19.284400497242594, -99.13830756897899) WHERE idSuc = 9;
UPDATE sucursal SET coordenada = POINT(19.403932539627704, -99.27285783276429) WHERE idSuc = 16;
UPDATE sucursal SET coordenada = POINT(19.39221096476124, -99.18357539116644) WHERE idSuc = 21;
UPDATE sucursal SET coordenada = POINT(19.441825738112588, -99.20575884625882) WHERE idSuc = 27;
UPDATE sucursal SET coordenada = POINT(19.506153352156268, -99.23632937450776) WHERE idSuc = 33;
UPDATE sucursal SET coordenada = POINT(19.257587629120433, -99.61626466344636) WHERE idSuc = 36;

-- productos nuevos
INSERT INTO producto (idProducto, nombre, marca, precioUnitario, idSubCat) VALUES 
    ("758104100422", "Bonafont 1L", "Bonafont", 10, 459),
    ("7891024027363", "Colgate Plax 60ml", "Colgate", 40, 459),
    ("7622210255341", "Tang pina colada", "Tang", 5, 459),
    ("7501058714398", "Lysol 650 mL", "Lysol", 80, 459),
    ("7702031887911", "Listerine zero alcohol 180mL", "Listerine", 45, 459);

UPDATE producto 
    SET img = 'https://www.superama.com.mx/Content/images/products/img_large/0075810410042L.jpg'
    WHERE idProducto = '758104100422';
UPDATE producto SET img = 'https://detqhtv6m6lzl.cloudfront.net/wp-content/uploads/2020/07/7891024027028-1.jpg' WHERE idProducto = '758104100422';
UPDATE producto SET img = 'https://http2.mlstatic.com/D_NQ_NP_733121-MLM32722606151_102019-O.jpg' WHERE idProducto = '7622210255341';
UPDATE producto SET img = 'https://www.laranitadelapaz.com.mx/images/thumbs/0006993_desinfectante-lysol-en-spray-pet-de-650ml_510.jpeg' WHERE idProducto = '7501058714398';
UPDATE producto SET img = 'https://resources.claroshop.com/medios-plazavip/s2/11073/1284131/5df96d4e54aed-7702031887942-1600x1600.jpg' WHERE idProducto = '7702031887911';


SELECT idProducto, nombre, marca FROM producto WHERE nombre LIKE "%nescafe%";
SELECT idProducto, nombre, marca FROM producto WHERE nombre LIKE "%maruchan%";
SELECT idProducto, nombre, marca FROM producto WHERE nombre LIKE "%doritos%";


-- hash 
-- dataset nuevo 
-- coordentadas