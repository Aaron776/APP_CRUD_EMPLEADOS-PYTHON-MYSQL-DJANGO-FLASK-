from flask import Flask, render_template, request, redirect,send_from_directory,url_for
from flaskext.mysql import MySQL
from datetime import datetime
import os     

app = Flask(__name__)
mysql = MySQL()

# Configuración de la base de datos MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema_empleados(python)'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Configuración de la carpeta de uploads
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)
   

@app.route('/')
def index():
    sql = "SELECT * FROM empleados"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    registros = cursor.fetchall()
    conn.close()  # Cierra la conexión después de usarla
    return render_template('empleados/index.html', empleados=registros)

@app.route('/crearEmpleados')
def crear_empleado():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    imagen = request.files['txtFoto']

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if imagen.filename != "":
        nuevoNombreImagen = tiempo + imagen.filename
        ruta_imagen = os.path.join(app.config['CARPETA'], nuevoNombreImagen)
        imagen.save(ruta_imagen)

    sql = "INSERT INTO empleados (id, nombre, correo, imagen) VALUES (NULL, %s, %s, %s)"
    datos = (nombre, correo, nuevoNombreImagen)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    conn.close()  # Cierra la conexión después de usarla
    return redirect('/')

@app.route('/eliminar/<int:id>')
def eliminar_registro(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT imagen FROM empleados WHERE id=%s', (id,))
    fila = cursor.fetchone()
    if fila is not None:
        imagen_a_borrar = os.path.join(app.config['CARPETA'], fila[0])
        if os.path.exists(imagen_a_borrar):
            os.remove(imagen_a_borrar)

    cursor.execute('DELETE FROM empleados WHERE id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/editar/<int:id>')
def editar_registro(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM empleados WHERE id=%s',(id))
    registro=cursor.fetchall()
    return render_template('empleados/edit.html',empleado=registro)

@app.route('/actualizar', methods=['POST'])
def actualizar_registro():
    id = request.form['txtID']
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    imagen = request.files['txtFoto']
    
    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s"
    datos = (nombre, correo, id)
    
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if imagen.filename != "":
        nuevoNombreImagen = tiempo + imagen.filename
        ruta_imagen = os.path.join(app.config['CARPETA'], nuevoNombreImagen)
        imagen.save(ruta_imagen)
        
        cursor.execute('SELECT imagen FROM empleados WHERE id=%s', (id,))
        fila = cursor.fetchone()
        if fila is not None:
            imagen_a_borrar = os.path.join(app.config['CARPETA'], fila[0])
            if os.path.exists(imagen_a_borrar):
                os.remove(imagen_a_borrar)
        
        cursor.execute('UPDATE empleados SET imagen=%s WHERE id=%s', (nuevoNombreImagen, id))
    
    cursor.execute(sql, datos)
    conn.commit()
    conn.close()
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)