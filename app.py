from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesaria para gestionar la sesión


# Datos de ejemplo del carrito de productos
carrito = [
    {'id': 1, 'nombre': 'Producto A', 'precio': 100, 'cantidad': 2},
    {'id': 2, 'nombre': 'Producto B', 'precio': 50, 'cantidad': 1}
]

# Configuración para guardar imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que la carpeta de subida existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('productos.db')
    conn.row_factory = sqlite3.Row
    return conn


# Ruta para inicializar la base de datos
@app.route('/initdb')
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL,
            imagen TEXT NOT NULL,
            unidades INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return "Base de datos inicializada correctamente."


# Ruta principal: Mostrar todos los productos
@app.route('/')
def index():
    conn = get_db_connection()
    productos = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return render_template('index.html', productos=productos)

# Agregar producto al carrito
@app.route('/agregar_carrito/<int:id>')
def agregar_carrito(id):
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()

    if producto and producto['unidades'] > 0:
        # Reducir unidades disponibles
        nuevas_unidades = producto['unidades'] - 1
        conn.execute('UPDATE productos SET unidades = ? WHERE id = ?', (nuevas_unidades, id))
        conn.commit()

        # Verificar si el producto tiene 0 unidades y eliminarlo
        if nuevas_unidades == 0:
            conn.execute('DELETE FROM productos WHERE id = ?', (id,))
            conn.commit()

        # Agregar al carrito
        if 'carrito' not in session:
            session['carrito'] = []
        session['carrito'].append({
            'id': producto['id'],
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'cantidad': 1
        })
        session.modified = True

    conn.close()
    return redirect(url_for('index'))