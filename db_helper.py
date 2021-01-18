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

    def get_products_info(self, raw_iids):
        self.cursor.execute('DESC producto')
        attrs = list(map(lambda x: x[0], self.cursor.fetchall()))
        attrs.append('nombreSubCat')

        query = f""" 
            SELECT 
                p.idProducto, p.nombre, p.marca, p.precioUnitario, p.idSubCat,
                s.nombre AS nombreSubCat
            FROM producto p, subcategoria s 
            WHERE p.idSubCat = s.idSubCat
                AND p.idProducto IN ( {', '.join(map(lambda x: '"' + x + '"', raw_iids))} )"""
        print(query)
        self.cursor.execute(query)

        res = []
        for info in (self.cursor.fetchall()):
            res.append({a: value for a, value in zip(attrs, info)})

        return {"productsInfo": res}

    def get_product_info(self, raw_iid):
        self.cursor.execute('DESC producto')
        attrs = list(map(lambda x: x[0], self.cursor.fetchall()))
        query = f"SELECT {', '.join(attrs)} FROM producto WHERE idProducto = %s"
        self.cursor.execute(query, raw_iid)
        return {a: value for a, value in zip(attrs, self.cursor.fetchone())}
        
    def insert_hist(self, req):
        uid, iids, amounts = req["idSocio"], req["idProductos"], req["cantidades"]
        res = {'success': False}
        try:
            insert_into = "INSERT INTO historial(idSocio, idProducto, cantidad) VALUES "
            vals = [f'''("{uid}", "{iid}", {cant})''' for iid, cant in zip(iids, amounts)]
            self.cursor.execute(insert_into + ', '.join(vals))
            self.conn.commit()
            res['success'] = True
        except Exception as e:
            print(e)
        finally:
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

    def insert_pendiente(self, req):
        uid, iid = req["idSocio"], req["idProducto"]
        res = {'success': False}
        try:
            insert_into = "INSERT INTO pendiente(idSocio, idProducto) VALUES (%s, %s)"
            self.cursor.execute(insert_into, (uid, iid))
            self.conn.commit()
            res['success'] = True
        except Exception as e:
            print(e)
        finally:
            return res

    def get_pendientes(self, uid):
        query = 'SELECT idProducto FROM pendiente WHERE idSocio = %s'
        iids = list(map(itemgetter(0), self.read(query, (uid))))
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

    def update_user(self, nombre, apPaterno, apMaterno, idSocio):
        query = ''' 
            UPDATE socio 
                SET nombre = %s, apPaterno = %s, apMaterno = %s
                WHERE idSocio = %s
         '''
        args = (nombre, apPaterno, apMaterno, idSocio)
        self.write(query, args)