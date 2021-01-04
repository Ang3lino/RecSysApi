
DROP PROCEDURE IF EXISTS insert_socio;
DELIMITER &
CREATE PROCEDURE insert_socio(
    IN p_apPaterno  varchar(30) ,
    IN p_apMaterno  varchar(30)  ,
    IN p_nombre     varchar(120) ,
    IN p_edad       int          ,
    IN p_genero     varchar(3)   ,
    IN p_email      varchar(40)  ,
    IN p_passwd     varchar(30)  
) BEGIN 
    -- SELECT LEFT(UUID(), 20);
    -- SELECT SUBSTRING(MD5(RAND()) FROM 1 FOR 20) AS myrandomstring;
    INSERT INTO socio (
        idSocio   ,
        apPaterno , 
        apMaterno , 
        nombre    , 
        edad      , 
        genero    , 
        email     , 
        passwd    
    ) VALUES (
        (SELECT SUBSTRING(MD5(RAND()) FROM 1 FOR 20)),
        p_apPaterno,
        p_apMaterno,
        p_nombre   ,
        p_edad     ,
        p_genero   ,
        p_email    ,
        p_passwd    
    );
    END &
DELIMITER ;

DROP PROCEDURE IF EXISTS do_login;
DELIMITER &
CREATE PROCEDURE do_login(
    IN p_email      varchar(40)  ,
    IN p_passwd     varchar(30)  
) BEGIN 
    SELECT count(*) FROM socio 
        WHERE email = p_email
            AND passwd = p_passwd
            ;
    END &
DELIMITER ;


