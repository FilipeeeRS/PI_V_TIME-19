import os
from dotenv import load_dotenv

# 1. Carrega as chaves secretas PRIMEIRO
load_dotenv()

# 2. Depois faz o resto das importações
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
import firebase_config
from firebase_admin import auth, firestore
from firebase_config import db
import pdfplumber
import io 
from services.gemini_services import gerar_conteudo
import json 

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
                'opcao': estudo.get('opcao', ''),
                'materia_id': estudo.get('materia_id', '')
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

    estudo_data = estudo_doc.to_dict()

    nome_materia = "Estudos" # Título padrão caso o estudo não tenha matéria
    materia_id = estudo_data.get('materia_id')
    
    if materia_id:
        materia_ref = db.collection('usuarios').document(uid).collection('materias').document(materia_id)
        materia_doc = materia_ref.get()
        if materia_doc.exists:
            nome_materia = materia_doc.to_dict().get('nome', 'Matéria Desconhecida')
    # ----------------------------------------------------

    return render_template(
        'estudo.html',
        pagina_ativa='estudo',
        estudo_id=estudo_id,
        estudo=estudo_data,
        nome_materia=nome_materia # Enviando a variável para o HTML
    )
    
@app.route('/materia/<materia_id>')
def visualizar_materia(materia_id):
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('login'))

    # Puxa os dados da matéria clicada
    materia_ref = db.collection('usuarios').document(uid).collection('materias').document(materia_id)
    materia_doc = materia_ref.get()

    if not materia_doc.exists:
        abort(404)

    materia_data = materia_doc.to_dict()
    materia_data['id'] = materia_doc.id

    # Puxa só os estudos que tem o id dessa matéria
    estudos_query = db.collection('usuarios').document(uid).collection('estudos').where('materia_id', '==', materia_id).stream()
    estudos_vinculados = [{'id': doc.id, **doc.to_dict()} for doc in estudos_query]

    return render_template(
        'materia.html', 
        pagina_ativa='materias', 
        materia=materia_data, 
        estudos_materia=estudos_vinculados
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
    
    # Pega todas as matérias do usuário
    materias_ref = db.collection('usuarios').document(uid).collection('materias').stream()
    materias = []
    
    for doc in materias_ref:
        materia_data = doc.to_dict()
        materia_data['id'] = doc.id
        
        # Pede pro banco de dados contar quantos estudos têm o ID desta matéria
        count_query = db.collection('usuarios').document(uid).collection('estudos').where('materia_id', '==', doc.id).count()
        results = count_query.get()
        materia_data['estudos'] = results[0][0].value
        
        materias.append(materia_data)
        
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

@app.route('/api/estudos/<estudo_id>', methods=['PUT'])
def renomear_estudo(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    data = request.get_json()
    novo_nome = data.get('nome')

    if novo_nome:
        db.collection('usuarios').document(uid).collection('estudos').document(estudo_id).update({
            'nome': novo_nome
        })
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'erro', 'mensagem': 'Nome não fornecido'}), 400

@app.route('/api/estudos/<estudo_id>/materia', methods=['PUT'])
def vincular_materia(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    data = request.get_json(silent=True) or {}
    materia_id = data.get('materia_id')

    if materia_id:
        db.collection('usuarios').document(uid).collection('estudos').document(estudo_id).update({
            'materia_id': materia_id
        })
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'erro', 'mensagem': 'Matéria não fornecida'}), 400

@app.route('/api/estudos/<estudo_id>/materia', methods=['DELETE'])
def desvincular_materia(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401
    
    # O firestore.DELETE_FIELD apaga o campo 'materia_id' daquele documento
    db.collection('usuarios').document(uid).collection('estudos').document(estudo_id).update({
        'materia_id': firestore.DELETE_FIELD
    })
    return jsonify({'status': 'ok'})

# CHECKLIST DE TÓPICOS: gera (1ª vez) ou retorna os tópicos salvos + estado de marcação
@app.route('/api/estudos/<estudo_id>/checklist', methods=['GET'])
def obter_checklist(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401

    doc_ref = db.collection('usuarios').document(uid).collection('estudos').document(estudo_id)
    snap = doc_ref.get()
    if not snap.exists:
        return jsonify({'status': 'erro', 'mensagem': 'Estudo não encontrado'}), 404

    estudo = snap.to_dict()
    checklist = estudo.get('checklist')

    # Já existe checklist salvo -> devolve direto
    if isinstance(checklist, list) and checklist:
        return jsonify({'status': 'ok', 'itens': checklist})

    # Senão, gera a partir do texto do material
    texto = estudo.get('texto', '')
    if not texto:
        return jsonify({'status': 'erro', 'mensagem': 'Este estudo não tem material para gerar a checklist.'}), 400

    resultado = gerar_conteudo('checklist_topicos', texto)

    itens = []
    for linha in resultado.split('\n'):
        t = linha.strip().lstrip('-*•0123456789.) ').strip()
        if t:
            itens.append({'texto': t, 'feito': False})

    if not itens:
        return jsonify({'status': 'erro', 'mensagem': 'Não foi possível gerar a checklist.'}), 500

    doc_ref.update({'checklist': itens})
    return jsonify({'status': 'ok', 'itens': itens})

# CHECKLIST DE TÓPICOS: salva o estado de marcação (o que já foi estudado)
@app.route('/api/estudos/<estudo_id>/checklist', methods=['PUT'])
def salvar_checklist(estudo_id):
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401

    data = request.get_json(silent=True) or {}
    itens = data.get('itens')
    if not isinstance(itens, list):
        return jsonify({'status': 'erro', 'mensagem': 'Formato inválido'}), 400

    # Sanitiza: mantém só texto + feito (bool)
    limpos = []
    for it in itens:
        if isinstance(it, dict) and it.get('texto'):
            limpos.append({'texto': str(it['texto']), 'feito': bool(it.get('feito'))})

    db.collection('usuarios').document(uid).collection('estudos').document(estudo_id).update({
        'checklist': limpos
    })
    return jsonify({'status': 'ok'})

### CRIAR NOVO ESTUDO - ATUALIZADO PARA SUPORTAR UPLOAD DENTRO DA MATÉRIA
@app.route('/api/processar', methods=['POST'])
def processar_pdf():
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401

    arquivo = request.files.get('arquivo')

    if not arquivo:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum arquivo enviado'}), 400

    nome = request.form.get('nome') or arquivo.filename

    # NOVO: Recebe o ID da matéria caso o upload venha diretamente da página da matéria
    materia_id_form = request.form.get('materia_id')

    texto = ''
    with pdfplumber.open(io.BytesIO(arquivo.read())) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += conteudo + '\n'

    if not texto.strip():
        return jsonify({
            'status': 'erro', 
            'mensagem': 'Este PDF contém imagens escaneadas e não possui texto legível. Por favor, envie um PDF com texto selecionável.'
        }), 400

    # Vincula à matéria somente se o upload veio de dentro de uma matéria.
    # Não cria nem sugere matéria automaticamente: só o usuário cria matérias.
    materia_id = materia_id_form

    estudo_ref = db.collection('usuarios').document(uid).collection('estudos').document()
    
    novo_estudo_data = {
        'nome': nome,
        'texto': texto,
        'conteudo': {}, 
        'criado_em': firestore.SERVER_TIMESTAMP
    }
    if materia_id:
        novo_estudo_data['materia_id'] = materia_id
        
    estudo_ref.set(novo_estudo_data)

    return jsonify({
        'status': 'ok',
        'redirect_url': url_for('visualizar_estudo', estudo_id=estudo_ref.id)
    })

# gerar resumo
@app.route('/api/gerar', methods=['POST'])
def gerar_conteudo_route():
    uid = session.get('uid')
    if not uid:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado'}), 401

    data = request.get_json()
    estudo_id = data.get('estudo_id')
    tipo = data.get('tipo')
    acao = data.get('acao', 'novo')

    doc_ref = db.collection('usuarios').document(uid).collection('estudos').document(estudo_id)
    snap = doc_ref.get()
    if not snap.exists:
        return jsonify({'status': 'erro', 'mensagem': 'Estudo não encontrado'}), 404
    estudo = snap.to_dict()
    texto = estudo.get('texto', '')

    # --- LÓGICA NOVA: QUESTÕES DO RESUMO ---
    tipo_ia = tipo
    tipo_salvar = tipo
    
    if tipo == 'questoes_resumo':
        texto = estudo.get('conteudo', {}).get('resumo', '')
        if not texto:
            return jsonify({'status': 'erro', 'mensagem': 'Por favor, gere um Resumo normal primeiro!'})
        tipo_ia = 'questoes' # Enganamos a IA para gerar questões no formato JSON
        tipo_salvar = 'questoes' # Guardamos como questões para ativar a interatividade do Quiz
        acao = 'novo' # Sobrescreve as questões antigas com as novas focadas no resumo

    # Puxa o conteúdo antigo do banco caso a ação seja 'mais'
    conteudo_existente = estudo.get('conteudo', {}).get(tipo_salvar, '') if acao == 'mais' else ''

    # Passa o histórico e o texto correto (PDF ou Resumo) para a IA
    resultado = gerar_conteudo(tipo_ia, texto, conteudo_existente)

    # Mescla o conteúdo novo com o antigo antes de salvar no Firebase
    conteudo_final = resultado
    if acao == 'mais' and conteudo_existente:
        if tipo_salvar == 'questoes':
            try:
                lista_antiga = json.loads(conteudo_existente)
                lista_nova = json.loads(resultado)
                conteudo_final = json.dumps(lista_antiga + lista_nova)
            except:
                pass
        else:
            conteudo_final = conteudo_existente + "\n\n" + resultado

    doc_ref.update({f'conteudo.{tipo_salvar}': conteudo_final})

    # O back-end devolve o tipo_render para o front-end saber renderizar as questoes interativas
    return jsonify({'status': 'ok', 'conteudo': conteudo_final, 'tipo_render': tipo_salvar})

if __name__ == '__main__':
    app.run(debug=True)