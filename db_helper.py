import pymysql


class DbHelper:
    def __init__(self, connection, cursor):
        self.cursor = cursor 
        self.conn = connection

    def login(self, email, passwd):
        self.cursor.execute('select passwd, idSocio from socio where email = %s ', email)
        passwd_id_from_db = self.cursor.fetchone()
        res = {'email_found': False, 'correct_passwd': False, 'idSocio': False}
        if passwd_id_from_db:
            res['email_found'] = True
            res['correct_passwd'] = passwd == passwd_id_from_db[0]
            if res['correct_passwd']:
                res['idSocio'] = passwd_id_from_db[1]
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
            return res

    def get_products_info(self, raw_iids):
        self.cursor.execute('DESC producto')
        attrs = list(map(lambda x: x[0], self.cursor.fetchall()))
        query = f"""SELECT {', '.join(attrs)} FROM producto 
                        WHERE idProducto in (
                                {', '.join(map(lambda x: '"' + x + '"', raw_iids))})"""
        self.cursor.execute(query)
        res = []
        for info in self.cursor.fetchall():
            res.append({a: value for a, value in zip(attrs, info)})
        return res

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

    def select(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete(self, query):
        self.cursor.execute(query)
        self.conn.commit()    

    