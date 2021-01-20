
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
ALTER TABLE socio ADD passwd VARCHAR(30) DEFAULT 'pass';
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

