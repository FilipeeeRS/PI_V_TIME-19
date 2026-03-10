from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_config
from firebase_admin import auth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'troque-por-uma-chave-secreta-forte')

@app.context_processor
def inject_session():
    return dict(session=session)

FIREBASE_CONFIG = {
    'firebase_api_key':            os.getenv('FIREBASE_API_KEY'),
    'firebase_auth_domain':        os.getenv('FIREBASE_AUTH_DOMAIN'),
    'firebase_project_id':         os.getenv('FIREBASE_PROJECT_ID'),
    'firebase_storage_bucket':     os.getenv('FIREBASE_STORAGE_BUCKET'),
    'firebase_messaging_sender_id':os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'firebase_app_id':             os.getenv('FIREBASE_APP_ID'),
}


@app.route('/')
def home():
    return render_template('bem_vindo.html')

@app.route('/home')
def home_page():
    return render_template('home.html', pagina_ativa='home')

@app.route('/login')
def login():
    return render_template('login.html', **FIREBASE_CONFIG)

@app.route('/registro')
def registro():
    return render_template('registro.html', **FIREBASE_CONFIG)

@app.route('/materias')
def materias():
    return render_template('materias.html', pagina_ativa='materias')

@app.route('/novo_estudo')
def novo_estudo():
    return render_template('novo_estudo.html', pagina_ativa='novo_estudo')

@app.route('/historico')
def historico():
    return render_template('historico.html', pagina_ativa='historico')


@app.route('/api/sessao', methods=['POST'])
def criar_sessao():
    """Recebe o ID token do Firebase (gerado no front) e cria sessão Flask."""
    data = request.get_json()
    id_token = data.get('idToken')

    try:
        decoded = auth.verify_id_token(id_token)
        session['uid']   = decoded['uid']
        session['email'] = decoded.get('email', '')
        session['nome']  = decoded.get('name', decoded.get('email', ''))
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)