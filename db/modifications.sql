
-- Modificacion para coincidencia con el csv
ALTER TABLE producto MODIFY idProducto VARCHAR(20);
ALTER TABLE producto MODIFY nombre VARCHAR(400);
ALTER TABLE producto MODIFY marca VARCHAR(100);

-- Modificacion de la llave primaria
show create table sociomembresia ;
ALTER TABLE sociomembresia DROP FOREIGN KEY sociomembresia_ibfk_1;
ALTER TABLE socio modify idSocio VARCHAR(40);
ALTER TABLE sociomembresia modify idSocio VARCHAR(40);
ALTER TABLE sociomembresia 
    ADD CONSTRAINT sociomembresia_ibfk_1 
    FOREIGN KEY (idSocio) REFERENCES socio (idSocio) 
    ON DELETE CASCADE ON UPDATE CASCADE;

-- Modificacion para coincidencia con el csv
alter table socio modify idSocio VARCHAR(40);
ALTER TABLE socio MODIFY nombre VARCHAR(120);

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
