from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from itsdangerous import URLSafeTimedSerializer as Serializer
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

# 🔐 Clave secreta para sesiones
app.secret_key = "advpjsh"

# 🗄 Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://dominguezjaneth206_db_user:noseque1@cluster0.tjxu1gh.mongodb.net/?retryWrites=true&w=majority")
db = client['Usuarios_bw']
collection = db['Usuarios']

# 📧 SendGrid (toma la API key del sistema)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Token seguro
serializer = Serializer(app.secret_key)


# -----------------------------
# 📩 FUNCIÓN PARA ENVIAR CORREO
# -----------------------------
def enviar_email(destinatario, asunto, cuerpo):
    mensaje = Mail(
        from_email='bisonweboficcial@gmail.com',
        to_emails=destinatario,
        subject=asunto,
        html_content=cuerpo
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mensaje)
        print(f"Correo enviado! Código: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


# -----------------------------
#            RUTAS
# -----------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))


# -----------------------------
# Registro
# -----------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        contrasena = request.form['contrasena']

        if collection.find_one({'email': email}):
            flash("El correo ya está registrado.", "error")
            return redirect(url_for('registro'))

        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')

        collection.insert_one({
            'usuario': usuario,
            'email': email,
            'contrasena': hashed_password
        })

        session['usuario'] = usuario
        return redirect(url_for('inicio'))

    return render_template('registrarse.html')


# -----------------------------
# Login
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        user = collection.find_one({'usuario': usuario})

        if user and bcrypt.check_password_hash(user['contrasena'], contrasena):
            session['usuario'] = usuario
            return redirect(url_for('inicio'))
        else:
            flash("Datos incorrectos.", "error")

    return render_template('index.html')


# -----------------------------
# Página principal
# -----------------------------
@app.route('/inicio')
def inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', usuario=session['usuario'])


# -----------------------------
# Perfil
# -----------------------------
@app.route('/mi_perfil')
def mi_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    user = collection.find_one({'usuario': session['usuario']})

    return render_template('mi_perfil.html', usuario=user['usuario'], email=user['email'])


# -----------------------------
# Recuperación de contraseña
# -----------------------------
@app.route('/Recuperar_contraseña', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form['email']
        usuario = collection.find_one({'email': email})

        if usuario:
            token = serializer.dumps(email)
            enlace = url_for('restablecer_contrasena', token=token, _external=True)

            asunto = "Recuperación de contraseña"
            cuerpo = f"""
                <h3>Restablecer contraseña</h3>
                <p>Haz clic en el enlace:</p>
                <a href="{enlace}">Restablecer contraseña</a>
            """

            enviar_email(email, asunto, cuerpo)
            flash("Correo enviado.", "success")
        else:
            flash("El correo no está registrado.", "error")

    return render_template('Recuperar_contraseña.html')


# -----------------------------
# Restablecer contraseña
# -----------------------------
@app.route('/Restablecer_contraseña/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    try:
        email = serializer.loads(token, max_age=3600)
    except:
        flash("El enlace expiró.", "error")
        return redirect(url_for('recuperar_contrasena'))

    if request.method == 'POST':
        nueva_contrasena = request.form['nueva_contrasena']
        hashed_password = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')

        collection.update_one({'email': email}, {'$set': {'contrasena': hashed_password}})

        flash("Contraseña actualizada!", "success")
        return redirect(url_for('login'))

    return render_template('Restablecer_contraseña.html')


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
