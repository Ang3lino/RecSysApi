
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
