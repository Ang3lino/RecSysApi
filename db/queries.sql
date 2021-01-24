
-- DROP DATABASE IF EXISTS costco ;
-- CREATE DATABASE costco;
-- USE costco;
-- SOURCE costco.sql;


SELECT c.nombre, COUNT(*) as count_prod
    FROM categoria c, subcategoria s, producto p
    WHERE c.idCat = s.idCat AND
        s.idSubCat = p.idSubCat 
    GROUP BY c.nombre 
    ORDER BY count_prod DESC
;


# 
SELECT c.nombre, s.nombre
    FROM categoria c, subcategoria s 
    WHERE c.idCat = s.idCat
        AND c.nombre = 'AUDIO'
;


# 
SELECT c.nombre, s.nombre, p.*
    FROM categoria c, subcategoria s, producto p
    WHERE c.idCat = s.idCat
        AND s.idSubCat = p.idSubCat
        AND c.nombre = 'SOFTWARE'
;

    INSERT INTO socio (
        idSocio   , 
        apPaterno , 
        apMaterno , 
        nombre     ,
        email
    ) VALUES (
        (SELECT SUBSTRING(MD5(RAND()) FROM 1 FOR 20)),
        'Lopez',
        'Enriquez',
        'Angel',
        'test@email.com'
    );

    INSERT INTO socio (
        idSocio   , 
        apPaterno , 
        apMaterno , 
        nombre     ,
        email
    ) VALUES (
        (SELECT SUBSTRING(MD5(RAND()) FROM 1 FOR 20)),
        'Lopez',
        'Morales',
        'Abigail',
        'almis@gmail.com'
    );

    INSERT INTO socio (
        idSocio   , 
        apPaterno , 
        apMaterno , 
        nombre     ,
        email
    ) VALUES (
        '7c716645d3d05615bf3d',
        'Lopez',
        'Morales',
        'Abigail',
        'almis@gmail.com'
    );


    call insert_socio(null, null, 'Naruto', 22, 'M', 'test@email.com', 'pass');
    select * from socio where email like 'test@email.com';
    -- IN p_apPaterno  varchar(30) ,
    -- IN p_apMaterno  varchar(30)  ,
    -- IN p_nombre     varchar(120) ,
    -- IN p_edad       int          ,
    -- IN p_genero     varchar(3)   ,
    -- IN p_email      varchar(40)  ,
    -- IN p_passwd     varchar(30) 

DELETE FROM socio WHERE email = 'almis@gmail.com';
-- mysqldump -u User -p DatabaseName > sqlfile.sql
-- mysqldump -u root -p costco > costco_ratings_software.sql


SELECT idSocio, nombre, apPaterno, apMaterno
    FROM socio
    LIMIT 5;

UPDATE socio 
    SET nombre = 'Alexander',
        apPaterno = 'Lopezz',
        apMaterno = 'Cerillo'
    WHERE idSocio = '0d412f801f6e3155e9cc'
;

SELECT * FROM valoracion 
    WHERE idSocio = "A0735469C3RVU9AWMDCE"
        AND idProducto = "B009KRW8JK"
;

SELECT 
    IF ((SELECT count(*) FROM valoracion 
            WHERE idSocio = "A0735469C3RVU9AWMDCE" AND idProducto = "B009KRW8JK") = 1, 
        "y", 
        "n") as valoro
;

SELECT 
    IF ((SELECT count(*) FROM valoracion 
            WHERE idSocio = %s AND idProducto = %s) = 1, 
        "y", 
        "n") as valoro
;

-- valoraciones donde se incluyen productos Hershey
SELECT v.* 
    FROM valoracion v, producto p 
    WHERE v.idProducto = p.idProducto 
        AND p.nombre LIKE "%Hershey%";

-- info de las sucursale de la CDMX y EDOMEX
SELECT s.idSuc, s.nombre, CONCAT(s.direccion, ' costco')
    FROM sucursal s, estado e 
    WHERE s.idEdo = e.idEdo 
        AND e.idEdo IN ((SELECT idEdo FROM estado WHERE nombre LIKE '%M_xico%'))
    ORDER BY s.idSuc;

-- seleccion de todas las coordenadas conocidas
SELECT ST_X(coordenada) as lat, ST_Y(coordenada) AS lgt 
    FROM sucursal
    WHERE coordenada IS NOT NULL;