from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
import firebase_config
from firebase_admin import auth, firestore
import os
from dotenv import load_dotenv
from firebase_config import db
import pdfplumber
import io 
from services.gemini_services import gerar_resumo


load_dotenv()
print("A CHAVE É:", os.getenv('FIREBASE_API_KEY'))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'troque-por-uma-chave-secreta-forte')

@app.context_processor
def inject_session():
    recentes = []
    uid = session.get('uid')

    if uid:
        estudos_ref = (
            db.collection('usuarios')
            .document(uid)
            .collection('estudos')
            .order_by('criado_em', direction=firestore.Query.DESCENDING)
            .limit(50)
        )

        for doc in estudos_ref.stream():
            estudo = doc.to_dict()
            recentes.append({
                'id': doc.id,
                'nome': estudo.get('nome', 'Estudo sem nome'),
                'opcao': estudo.get('opcao', '')
            })

    return dict(session=session, estudos_recentes=recentes)

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
    return redirect(url_for('home_page'))

@app.route('/estudo/<estudo_id>')
def visualizar_estudo(estudo_id):
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('login'))

    estudo_ref = db.collection('usuarios').document(uid).collection('estudos').document(estudo_id)
    estudo_doc = estudo_ref.get()

    if not estudo_doc.exists:
        abort(404)

    return render_template(
        'estudo.html',
        pagina_ativa='estudo',
        estudo_id=estudo_id,
        estudo=estudo_doc.to_dict()
    )


@app.route('/api/sessao', methods=['POST'])
def criar_sessao():
    """Recebe o ID token do Firebase (gerado no front) e cria sessão Flask."""
    data = request.get_json()
    id_token = data.get('idToken')

    try:
        decoded = auth.verify_id_token(id_token)
        session['uid']   = decoded['uid']
        session['email'] = decoded.get('email', '')
        session['nome'] = decoded.get('name') or decoded.get('email', '')
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/materias', methods=['GET'])
def listar_materias(): 
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    materias_ref = db.collection('usuarios').document(uid).collection('materias')
    materias = [{'id': doc.id, **doc.to_dict()} for doc in materias_ref.stream()]
    return jsonify(materias)

@app.route('/api/materias', methods=['POST'])
def criar_materia():
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    data = request.get_json()
    nome = data.get('nome', '').strip()
    cor = data.get('cor', 'c-blue')
    
    if not nome:
        return jsonify({'status': 'erro', 'mensagem': 'Nome obrigatório'}), 400
    
    materias_ref = db.collection('usuarios').document(uid).collection('materias')
    doc = materias_ref.add({'nome': nome, 'cor': cor, 'estudos': 0})
    return jsonify({'status': 'ok', 'id': doc[1].id})

@app.route('/api/materias/<materia_id>', methods=['DELETE'])
def deletar_materia(materia_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    db.collection('usuarios').document(uid).collection('materias').document(materia_id).delete()
    return jsonify({'status': 'ok'})

@app.route('/api/estudos/<estudo_id>', methods=['DELETE'])
def deletar_estudo(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    db.collection('usuarios').document(uid).collection('estudos').document(estudo_id).delete()
    return jsonify({'status': 'ok'})

### criar novo estudo
@app.route('/api/processar', methods=['POST'])
def processar_pdf():
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401

    arquivo = request.files.get('arquivo')
    nome = request.form.get('nome') or arquivo.filename

    if not arquivo:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo enviado'}), 400

    # Extrai o texto do PDF
    texto = ''
    with pdfplumber.open(io.BytesIO(arquivo.read())) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += conteudo + '\n'

    if not texto.strip():
        return jsonify({'status': 'erro', 'mensagem': 'Não foi possível extrair texto do PDF'}), 400

    estudo_ref = db.collection('usuarios').document(uid).collection('estudos').document()
    
    estudo_ref.set({
        'nome': nome,
        'texto': texto,
        'conteudo': {}, # fazer dps com a IA
        'criado_em': firestore.SERVER_TIMESTAMP
    })

    return jsonify({
        'status': 'ok',
        'redirect_url': url_for('visualizar_estudo', estudo_id=estudo_ref.id)
    })

# gerar resumo
@app.route('/api/gerar', methods=['POST'])
def gerar_conteudo():
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro'}), 401

    data = request.get_json()
    estudo_id = data.get('estudo_id')
    tipo = data.get('tipo')

    doc_ref = db.collection('usuarios').document(uid).collection('estudos').document(estudo_id)
    estudo = doc_ref.get().to_dict()

    texto = estudo.get('texto')

    if tipo == 'resumo':
        resultado = gerar_resumo(texto)

        doc_ref.update({
            'conteudo.resumo': resultado
        })

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
