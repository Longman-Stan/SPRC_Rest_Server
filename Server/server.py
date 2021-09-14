from flask import Flask, request, jsonify, Response
import psycopg2
import datetime as dt

app = Flask("Tema2_server")
hostname = "postgres_db_container"
port = "5432"
db_name = "Tema2"
username = "Tema2_user"
password = "1234"

db_connection = psycopg2.connect(host = hostname, port = port, dbname = db_name, user = username, password = password)
db_cursor = db_connection.cursor()

@app.route("/test", methods = ["GET"])
def test():
    return jsonify("hello"), 200


NAME = 0
TYPE = 1
def check_json(list, json_file):
    for param in list:
        if param[NAME] not in json_file:
            return False
        elif param[TYPE] is not type(json_file[param[NAME]]):
            if param[TYPE] is float and type(json_file[param[NAME]]) is int:
                continue
            return False
    return True

def get_record(list, json_file):
    rez = []
    for param in list:
        rez.append( json_file[param[NAME]])
    return tuple(rez)

def make_dict(list, elems):
    res = {}
    for i in range(len(list)):
        name, typeof = list[i]
        if name is None:
            continue
        res[name] = typeof(elems[i])
    return res

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"Countries"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
countries_name_types_list = [ ("nume", str) , ("lat", float), ("lon", float)]
countries_update_name_types_list = countries_name_types_list + [ ("id", int)]
countries_get_list = [ ("id", int)] + countries_name_types_list
countries_insert = """ INSERT INTO Tari (nume_tara, latitudine, \
                    longitudine) VALUES (%s,%s,%s)"""
countries_insert_with_id = """ INSERT INTO Tari (id, nume_tara, latitudine, \
                    longitudine) VALUES (%s,%s,%s,%s)"""
countries_get = """ SELECT * from Tari"""
countries_get_check_existance = """ SELECT * from Tari where id = %s"""
countries_delete = """DELETE from Tari where id = %s"""
countries_update = """UPDATE Tari set nume_tara = %s, latitudine = %s, longitudine = %s where id = %s"""

@app.route("/api/countries", methods = ["POST"])
def add_country():
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json( countries_name_types_list, payload):
        return Response(status = 400)
    record = get_record(countries_name_types_list, payload)
    try:
        db_cursor.execute(countries_insert, record)
        db_connection.commit()
        db_cursor.execute('SELECT LASTVAL()')
        id = db_cursor.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la inserare tari", error)
        return Response(status = 409)
    response = { 'id' : id}
    return jsonify(response), 201

@app.route("/api/countries", methods = ["GET"])
def get_countries():
    try:
        db_cursor.execute(countries_get)
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get tari", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(countries_get_list, row))
    return jsonify(result), 200

@app.route("/api/countries/<int:id>", methods = ["PUT"])
def update_country(id):
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json( countries_update_name_types_list, payload):
        return Response(status = 400)
    if id != payload["id"]:
        return Response(status = 400)
    record = get_record(countries_update_name_types_list, payload)
    try:
        db_cursor.execute(countries_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)    
        db_cursor.execute(countries_update, record)
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la update tari", error)
        return Response(status = 409)
    return Response(status = 200)

@app.route("/api/countries/<int:id>", methods = ["DELETE"])
def delete_country(id):
    try:
        db_cursor.execute(countries_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)
        db_cursor.execute(countries_delete, [id])
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("conflict la stergere tari", error)
        return Response(status = 404)
    return Response(status = 200)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"Cities"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cities_name_types_list = [ ("idTara", int), ("nume", str) , ("lat", float), ("lon", float)]
cities_get_types_list = [("id",int)] + cities_name_types_list
cities_update_name_types_list =  cities_name_types_list + [ ("id", int)]
cities_get_from_country_list = [ ("id", int), (None, None), ("nume", str) , ("lat", float), ("lon", float)]
cities_insert = """ INSERT INTO Orase (id_tara, nume_oras, latitudine, \
                    longitudine) VALUES (%s,%s,%s,%s)"""
cities_insert_with_id = """ INSERT INTO Orase (id, id_tara, nume_oras, latitudine, \
                    longitudine) VALUES (%s,%s,%s,%s,%s)"""
cities_get_all = """ SELECT * from Orase"""
cities_get = """ SELECT * from Orase where id_tara = %s"""
cities_get_check_existance = """ SELECT * from Orase where id = %s"""
cities_delete = """DELETE from Orase where id = %s"""
cities_update = """UPDATE Orase set id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s where id = %s"""
tara_verif = """Select * from Tari where id = %s"""

@app.route("/api/cities", methods = ["POST"])
def add_city():
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json( cities_name_types_list, payload):
        return Response(status = 400)
    record = get_record(cities_name_types_list, payload)
    try:
        db_cursor.execute(tara_verif, [record[0]])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        return Response(status = 404)

    try:
        db_cursor.execute(cities_insert, record)
        db_connection.commit()
        db_cursor.execute('SELECT LASTVAL()')
        id = db_cursor.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la inserare oras", error)
        return Response(status = 409)
    response = { 'id' : id}
    return jsonify(response), 201

@app.route("/api/cities", methods = ["GET"])
def get_all_cities():
    try:
        db_cursor.execute(cities_get_all)
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get toate orasele", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(cities_get_types_list, row))
    return jsonify(result), 200

@app.route("/api/cities/country/<int:id>", methods = ["GET"])
def get_cities(id):
    try:
        db_cursor.execute(cities_get, [id])
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get toate orasele", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(cities_get_from_country_list, row))
    return jsonify(result), 200

@app.route("/api/cities/<int:id>", methods = ["PUT"])
def update_city(id):
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json(cities_update_name_types_list, payload):
        return Response(status = 400)
    if id != payload["id"]:
        return Response(status = 400)
    record = get_record(cities_update_name_types_list, payload)
    try:
        db_cursor.execute(cities_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)    
        db_cursor.execute(cities_update, record)
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la update oras", error)
        return Response(status = 409)
    return Response(status = 200)

@app.route("/api/cities/<int:id>", methods = ["DELETE"])
def delete_city(id):
    try:
        db_cursor.execute(cities_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)
        db_cursor.execute(cities_delete, [id])
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("conflict la stergere oras", error)
        return Response(status = 404)
    return Response(status = 200)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"Temperatures"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
temp_name_types_list = [ ("idOras", int), ("valoare", float)]
temp_name_types_list_timestamp = [ ("valoare", float), ("timestamp", str), ("idOras", int)]
temp_update_name_types_list =  [ ("valoare", float), ("idOras", int), ("id", int)]
temp_payload_update = [ ("id", int)] + temp_name_types_list
temp_get_from_country_list = [ ("id", int), ("valoare", float), ("timestamp", str)]

temp_insert = """ INSERT INTO Temperaturi (valoare, timestamp, \
                    id_oras) VALUES (%s,%s,%s)"""
temp_insert_with_id = """ INSERT INTO Temperaturi (id, valoare, timestamp, id_oras) \
                        VALUES (%s,%s,%s,%s)"""

temp_get_lat_long = """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t\
                            INNER JOIN Orase s on t.id_oras = s.id\
                        Where s.latitudine = %s and s.longitudine = %s
                            and t.timestamp between %s and %s"""
temp_get_lat = """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t\
                            INNER JOIN Orase s on t.id_oras = s.id\
                        Where s.latitudine = %s and t.timestamp between %s and %s"""
temp_get_long = """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t\
                            INNER JOIN Orase s on t.id_oras = s.id\
                        Where s.longitudine = %s and t.timestamp between %s and %s"""
temp_get_all_time =  """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t
                        where t.timestamp between %s and %s"""

temp_get_oras = """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t\
                            INNER JOIN Orase s on t.id_oras = s.id\
                        Where t.id_oras = %s and t.timestamp between %s and %s"""

temp_get_tara = """ SELECT t.id, t.valoare, t.timestamp\
                        from Temperaturi t\
                            INNER JOIN Orase s on t.id_oras = s.id\
                        Where s.id_tara = %s and t.timestamp between %s and %s"""

temp_get_check_existance = """ SELECT * from Temperaturi where id = %s"""
temp_delete = """DELETE from Temperaturi where id = %s"""
temp_update = """UPDATE Temperaturi set valoare = %s, id_oras = %s where id = %s"""
cities_verif = """SELECT * from Orase where id = %s"""

@app.route("/api/temperatures", methods = ["POST"])
def add_temperature():
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json( temp_name_types_list, payload):
        return Response(status = 400)
    payload["timestamp"] = str(dt.datetime.now())
    record = get_record(temp_name_types_list_timestamp, payload)
    try:
        db_cursor.execute(cities_verif, [record[-1]])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        return Response(status = 404)
    try:
        db_cursor.execute(temp_insert, record)
        db_connection.commit()
        db_cursor.execute('SELECT LASTVAL()')
        id = db_cursor.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la inserare temepratura", error)
        return Response(status = 409)
    response = { 'id' : id}
    return jsonify(response), 201

def modify_time(query, frm, until, no_and = False):
    if frm is not None and until is not None:
        return query
    query = query[:-34]
    put_and = " and "
    if no_and:
        query = query[:-1]
        put_and = "where "
    if frm is not None:
        return query + put_and + "t.timestamp >= %s"
    if until is not None:
        return query + put_and + "t.timestamp <= %s"
    return query

def build_response_from_args(*args):
    sol = []
    for arg in args:
        if arg is not None:
            sol.append(arg)
    return tuple(sol)

@app.route("/api/temperatures", methods = ["GET"])
def get_temps_lat_long():
    lat = request.args.get('lat', default= None, type = str)
    lon = request.args.get('lon', default= None, type = str)
    frm = request.args.get('from', default= None, type = str)
    until = request.args.get('until', default= None, type = str)
    query = temp_get_lat_long
    no_and = False
    if lat is None and lon is None:
        query = temp_get_all_time
        no_and = True
    else:
        if lat is None:
            query = temp_get_long
        if lon is None:
            query = temp_get_lat
    query = modify_time(query, frm, until, no_and)
    params = build_response_from_args(lat,lon,frm,until)
    try:
        db_cursor.execute(query, params)
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get toate orasele", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(temp_get_from_country_list, row))
    return jsonify(result), 200

@app.route("/api/temperatures/cities/<int:idOras>", methods = ["GET"])
def get_temps_idOras(idOras):
    frm = request.args.get('from', default= None, type = str)
    until = request.args.get('until', default= None, type = str)
    query = temp_get_oras
    query = modify_time(query, frm, until)
    params = build_response_from_args(idOras,frm,until)
    try:
        db_cursor.execute(query, params)
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get toate orasele", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(temp_get_from_country_list, row))
    return jsonify(result), 200

@app.route("/api/temperatures/countries/<int:idTara>", methods = ["GET"])
def get_temps_idTara(idTara):
    frm = request.args.get('from', default= None, type = str)
    until = request.args.get('until', default= None, type = str)
    query = temp_get_tara
    query = modify_time(query, frm, until)
    params = build_response_from_args(idTara,frm,until)
    try:
        db_cursor.execute(query, params)
        records = db_cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("problema get toate orasele", error)
        return jsonify([]), 200
    result = []
    for row in records:
        result.append(make_dict(temp_get_from_country_list, row))
    return jsonify(result), 200

@app.route("/api/temperatures/<int:id>", methods = ["PUT"])
def update_temperature(id):
    payload = request.get_json(silent = True)
    if not payload:
        return Response(status = 400)
    if not check_json(temp_payload_update, payload):
        return Response(status = 400)
    if id != payload["id"]:
        return Response(status = 400)
    record = get_record(temp_update_name_types_list, payload)
    try:
        db_cursor.execute(temp_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)    
        db_cursor.execute(temp_update, record)
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        db_connection.rollback()
        print("conflict la update temperatura", error)
        return Response(status = 409)
    return Response(status = 200)

@app.route("/api/temperatures/<int:id>", methods = ["DELETE"])
def delete_temperature(id):
    try:
        db_cursor.execute(temp_get_check_existance, [id])
        records = db_cursor.fetchall()
        if len(records) == 0:
            return Response(status = 404)
        db_cursor.execute(temp_delete, [id])
        db_connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("conflict la stergere oras", error)
        return Response(status = 404)
    return Response(status = 200)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)