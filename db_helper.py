import pymysql
from operator import itemgetter


class DbHelper:
    def __init__(self, connection, cursor):
        self.cursor = cursor 
        self.conn = connection

    def login(self, email, passwd):
        self.cursor.execute('DESC socio')
        attrs = list(map(itemgetter(0), self.cursor.fetchall()))
        query = f"""SELECT {', '.join(attrs)} FROM socio WHERE email = %s AND passwd = %s"""
        self.cursor.execute(query, (email, passwd))
        socio_from_db = self.cursor.fetchone()
        res = {'ok': False}
        if socio_from_db:
            res['socio'] = {attr: info for attr, info in zip(attrs, socio_from_db)}
            res['ok'] = True
        return res

    def register(self, socio):
        '''
        Args: 
            Socio es un diccionario con atributos 
            ('apPaterno', 'apMaterno', 'nombre', 'edad', 'genero', 'email', 'passwd')
        Return:
            Diccionario donde el valor para la clave 'email_used' es True si ya 
            existe un email por ingresar, valor para success True en caso de 
            hacer el registro correctamente.
        '''
        res = {'email_used': False, 'success': False}
        try:
            args_order = ('apPaterno', 'apMaterno', 'nombre', 'edad', 'genero', 'email', 'passwd')
            args = tuple(socio[arg] for arg in args_order)
            self.cursor.callproc('insert_socio', args)
            res['success'] = True
        except pymysql.err.IntegrityError as err:
            if 'c_uniq_email_passwd' in str(err):
                res['email_used'] = True
            print(err)
        finally:
            self.conn.commit()    
            res['socio'] = self.login(socio['email'], socio['passwd'])
            return res

    def get_products_info(self, raw_iids: list, extra_info: dict):
        if raw_iids:  # if non empty LIST
            self.cursor.execute('DESC producto')
            attrs = list(map(lambda x: x[0], self.cursor.fetchall()))
            attrs.append('nombreSubCat')

            query = f""" 
                SELECT 
                    p.idProducto, p.nombre, p.marca, p.precioUnitario, p.idSubCat, p.img,
                    s.nombre AS nombreSubCat
                FROM producto p, subcategoria s 
                WHERE p.idSubCat = s.idSubCat
                    AND p.idProducto IN ( {', '.join(map(lambda x: '"' + x + '"', raw_iids))} )"""
            self.cursor.execute(query)

            res = []
            for info in (self.cursor.fetchall()):
                p_info = {a: value for a, value in zip(attrs, info)}
                p_info.update(extra_info)
                res.append(p_info)

            return {"productsInfo": res}
        raise Exception("get_products_info: raw_iids esta vacia")

    def get_product_info(self, iid, uid=None):
        attrs = list(map(lambda x: x[0], self.read('DESC producto')))
        query = f"SELECT {', '.join(attrs)} FROM producto WHERE idProducto = %s"
        resultset = self.read(query, (iid))  # retrieve tuple of values
        if resultset == ():  
            raise Exception(f'iid = {iid} does not exists in the database')
        res = {a: value for a, value in zip(attrs, resultset[0])}
        if uid:
            query = """ SELECT IF ((SELECT count(*) FROM valoracion 
                                WHERE idSocio = %s AND idProducto = %s) = 1, 
                            "y", 
                            "n") as valoro
                    """
            res['valoracion'] = self.read(query, (uid, iid))[0][0]  # first row, first column
        return res 

    def insert_hist(self, uid, iids, amounts):
        insert_into = "INSERT INTO historial(idSocio, idProducto, cantidad) VALUES "
        vals = [f'''("{uid}", "{iid}", {cant})''' for iid, cant in zip(iids, amounts)]
        self.cursor.execute(insert_into + ', '.join(vals))
        self.conn.commit()

        select = """
                SELECT fecha_hora FROM historial
                    WHERE idSocio = %s
                    ORDER BY 1 DESC"""
        res = {'fecha_hora': self.read(select, (uid))[0][0]}
        return res

    def __get_attr_names(self, tablename):
        self.cursor.execute(f'DESC {tablename}')
        return list(map(itemgetter(0), self.cursor.fetchall()))
    
    def __flat_tuples(self, tuples, attrs):
        return {attr: list(map(itemgetter(i), tuples)) for i, attr in enumerate(attrs)}

    def get_purchases(self, uid):
        attrs = self.__get_attr_names('historial')
        select = "SELECT " + ', '.join(attrs) + " FROM historial WHERE idSocio = %s"
        return self.__flat_tuples(self.read(select, (uid)), attrs)

    def insert_pendiente(self, uid, iid):
        insert_into = "INSERT INTO pendiente(idSocio, idProducto) VALUES (%s, %s)"
        self.cursor.execute(insert_into, (uid, iid))
        self.conn.commit()

    def get_pendientes(self, uid):
        query = 'SELECT idProducto FROM pendiente WHERE idSocio = %s'
        resultset = self.read(query, (uid))
        iids = list(map(itemgetter(0), resultset))
        return self.get_products_info(iids)
    
    def insert_rating(self, uid, iid, rating):
        query = "INSERT INTO valoracion(idSocio, idProducto, rating) VALUES (%s, %s, %s)"
        self.write(query, (uid, iid, rating))

    def get_ratings(self, uid):
        attrs = ['idProducto', 'rating']
        query = f"SELECT {(', ').join(attrs)} FROM valoracion WHERE idSocio = %s"
        iids, ratings = [], []
        for iid, rat in self.read(query, (uid)):
            iids.append(iid)
            ratings.append(iid)
        return {'iids': iids, 'ratings': ratings}

    def read(self, query, args=None):
        if args:
            self.cursor.execute(query, args)
        else:
            self.cursor.execute(query, )
        return self.cursor.fetchall()

    def write(self, query, args=None):
        if args:
            self.cursor.execute(query, args)
        else:
            self.cursor.execute(query, )
        self.conn.commit()    

    def get_ticket_info(self,uid, iid,date):
        query = '''SELECT a.idProducto, b.nombre, a.cantidad, b.precioUnitario FROM(
SELECT idProducto,cantidad
FROM historial 
WHERE idSocio = %s and fecha_hora = %s
group by idSocio,fecha_hora,idProducto,cantidad
)A inner join producto b on a.idProducto=b.idProducto '''
        products=[]
        for [id,nom,can,pre] in self.read(query, (uid,date)):
            products.append([id,nom,can,pre])
        return products

    def get_tickets_info(self,uid):
        query = '''SELECT a.idProducto, b.nombre, a.cantidad, b.precioUnitario,a.fecha_hora FROM(
SELECT idProducto,cantidad,fecha_hora
FROM historial 
WHERE idSocio = %s
group by idSocio,fecha_hora,idProducto,cantidad
)A inner join producto b on a.idProducto=b.idProducto '''
        products=[]
        for [id,nom,can,pre,fecha] in self.read(query, (uid)):
            products.append([id,nom,can,pre,fecha])
        return products

    def update_user(self, nombre, apPaterno, apMaterno, idSocio):
        query = ''' 
            UPDATE socio 
                SET nombre = %s, apPaterno = %s, apMaterno = %s
                WHERE idSocio = %s
         '''
        args = (nombre, apPaterno, apMaterno, idSocio)
        self.write(query, args)

    