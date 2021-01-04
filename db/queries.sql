
DROP DATABASE IF EXISTS costco ;

CREATE DATABASE costco;
USE costco;

SOURCE costco.sql;


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



