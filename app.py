from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enempro-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enempro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token expirado'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Token inválido'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Token não fornecido'}), 401

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    apelido = db.Column(db.String(50), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    escolaridade = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    senha = db.Column(db.String(255), nullable=False)
    aceitou_termos = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conteudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    link = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    links = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Simulado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pergunta = db.Column(db.Text, nullable=False)
    correta = db.Column(db.String(1), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    publica = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SimuladoQuestao(db.Model):
    simulado_id = db.Column(db.Integer, db.ForeignKey('simulado.id'), primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'), primary_key=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/conteudos')
def conteudos_page():
    return render_template('conteudos.html')

@app.route('/flashcards')
def flashcards_page():
    return render_template('flashcards.html')

@app.route('/simulados')
def simulados_page():
    return render_template('simulados.html')

@app.route('/questoes')
def questoes_page():
    return render_template('questoes.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/relatorios')
def relatorios_page():
    return render_template('relatorios.html')

@app.route('/perfil')
def perfil_page():
    return render_template('perfil.html')

@app.route('/recuperar-senha')
def recuperar_senha_page():
    return render_template('recuperar_senha.html')

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        usuario = Usuario(
            nome_completo=data['nome_completo'],
            apelido=data['apelido'],
            data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date(),
            escolaridade=data['escolaridade'],
            email=data['email'],
            telefone=data.get('telefone', ''),
            senha=generate_password_hash(data['senha']),
            aceitou_termos=data['aceitou_termos']
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'id': usuario.id,
            'message': 'Usuário criado com sucesso'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        usuario = Usuario.query.filter_by(email=data['email']).first()
        
        if usuario and check_password_hash(usuario.senha, data['senha']):
            access_token = create_access_token(identity=str(usuario.id))
            return jsonify({
                'token': access_token,
                'user_id': usuario.id,
                'apelido': usuario.apelido
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_me():
    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        return jsonify({
            'id': usuario.id,
            'nome_completo': usuario.nome_completo,
            'apelido': usuario.apelido,
            'data_nascimento': usuario.data_nascimento.isoformat(),
            'escolaridade': usuario.escolaridade,
            'email': usuario.email,
            'telefone': usuario.telefone or '',
            'aceitou_termos': usuario.aceitou_termos,
            'is_admin': usuario.is_admin,
            'created_at': usuario.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        return jsonify({
            'id': usuario.id,
            'nome_completo': usuario.nome_completo,
            'apelido': usuario.apelido,
            'data_nascimento': usuario.data_nascimento.isoformat(),
            'escolaridade': usuario.escolaridade,
            'email': usuario.email,
            'telefone': usuario.telefone or '',
            'aceitou_termos': usuario.aceitou_termos,
            'is_admin': usuario.is_admin,
            'created_at': usuario.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/perfil', methods=['PUT'])
@jwt_required()
def update_perfil():
    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        data = request.get_json()
        
        if 'apelido' in data:
            usuario.apelido = data['apelido']
        if 'escolaridade' in data:
            usuario.escolaridade = data['escolaridade']
        if 'nome_completo' in data:
            usuario.nome_completo = data['nome_completo']
        if 'email' in data:
            existing_user = Usuario.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email já cadastrado'}), 400
            usuario.email = data['email']
        if 'telefone' in data:
            usuario.telefone = data['telefone']
        if 'data_nascimento' in data:
            usuario.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        if 'senha' in data and data['senha']:
            usuario.senha = generate_password_hash(data['senha'])
            
        db.session.commit()
        
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/perfil', methods=['DELETE'])
@jwt_required()
def delete_perfil():
    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Perfil deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/recuperar', methods=['POST'])
def recuperar_senha():
    try:
        data = request.get_json()
        
        if 'nova_senha' in data:
            usuario = Usuario.query.filter_by(email=data['email']).first()
            
            if not usuario:
                return jsonify({'error': 'Email não encontrado'}), 404
            
            usuario.senha = generate_password_hash(data['nova_senha'])
            db.session.commit()
            
            return jsonify({'message': 'Senha redefinida com sucesso'}), 200
        else:
            usuario = Usuario.query.filter_by(
                email=data['email'],
                telefone=data['telefone']
            ).first()
            
            if usuario:
                return jsonify({'message': 'Dados verificados. Você pode redefinir sua senha.'}), 200
            else:
                return jsonify({'error': 'Email ou telefone não conferem'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conteudos', methods=['POST'])
@jwt_required()
def criar_conteudo():
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        conteudo = Conteudo(
            nome=data['nome'],
            descricao=data['descricao'],
            link=data['link'],
            tipo=data['tipo'],
            user_id=user_id
        )
        
        db.session.add(conteudo)
        db.session.commit()
        
        return jsonify({
            'id': conteudo.id,
            'message': 'Conteúdo criado com sucesso'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conteudos', methods=['GET'])
def listar_conteudos():
    try:
        conteudos = Conteudo.query.all()
        return jsonify([{
            'id': c.id,
            'tipo': c.tipo,
            'nome': c.nome,
            'descricao': c.descricao,
            'created_at': c.created_at.isoformat(),
            'updated_at': c.updated_at.isoformat(),
            'user_id': c.user_id
        } for c in conteudos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conteudos/<int:id>', methods=['GET'])
def get_conteudo(id):
    try:
        conteudo = Conteudo.query.get(id)
        if not conteudo:
            return jsonify({'error': 'Conteúdo não encontrado'}), 404
            
        return jsonify({
            'id': conteudo.id,
            'tipo': conteudo.tipo,
            'nome': conteudo.nome,
            'descricao': conteudo.descricao,
            'link': conteudo.link,
            'created_at': conteudo.created_at.isoformat(),
            'updated_at': conteudo.updated_at.isoformat(),
            'user_id': conteudo.user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conteudos/<int:id>', methods=['PUT'])
@jwt_required()
def update_conteudo(id):
    try:
        conteudo = Conteudo.query.get(id)
        if not conteudo:
            return jsonify({'error': 'Conteúdo não encontrado'}), 404
            
        data = request.get_json()
        
        if 'nome' in data:
            conteudo.nome = data['nome']
        if 'descricao' in data:
            conteudo.descricao = data['descricao']
        if 'link' in data:
            conteudo.link = data['link']
        if 'tipo' in data:
            conteudo.tipo = data['tipo']
            
        db.session.commit()
        
        return jsonify({'message': 'Conteúdo atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conteudos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_conteudo(id):
    try:
        conteudo = Conteudo.query.get(id)
        if not conteudo:
            return jsonify({'error': 'Conteúdo não encontrado'}), 404
            
        db.session.delete(conteudo)
        db.session.commit()
        
        return jsonify({'message': 'Conteúdo deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/flashcards', methods=['POST'])
@jwt_required()
def criar_flashcard():
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        flashcard = Flashcard(
            nome=data['nome'],
            descricao=data['descricao'],
            links=json.dumps(data.get('links', [])),
            user_id=user_id
        )
        
        db.session.add(flashcard)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard criado com sucesso'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/flashcards', methods=['GET'])
@jwt_required()
def listar_flashcards():
    try:
        user_id = int(get_jwt_identity())
        flashcards = Flashcard.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            'id': f.id,
            'nome': f.nome,
            'created_at': f.created_at.isoformat(),
            'updated_at': f.updated_at.isoformat()
        } for f in flashcards]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/flashcards/<int:id>', methods=['GET'])
@jwt_required()
def get_flashcard(id):
    try:
        flashcard = Flashcard.query.get(id)
        if not flashcard:
            return jsonify({'error': 'Flashcard não encontrado'}), 404
            
        return jsonify({
            'id': flashcard.id,
            'nome': flashcard.nome,
            'descricao': flashcard.descricao,
            'links': json.loads(flashcard.links) if flashcard.links else [],
            'created_at': flashcard.created_at.isoformat(),
            'updated_at': flashcard.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/flashcards/<int:id>', methods=['PUT'])
@jwt_required()
def update_flashcard(id):
    try:
        flashcard = Flashcard.query.get(id)
        if not flashcard:
            return jsonify({'error': 'Flashcard não encontrado'}), 404
            
        data = request.get_json()
        
        if 'nome' in data:
            flashcard.nome = data['nome']
        if 'descricao' in data:
            flashcard.descricao = data['descricao']
        if 'links' in data:
            flashcard.links = json.dumps(data['links'])
            
        db.session.commit()
        
        return jsonify({'message': 'Flashcard atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/flashcards/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_flashcard(id):
    try:
        flashcard = Flashcard.query.get(id)
        if not flashcard:
            return jsonify({'error': 'Flashcard não encontrado'}), 404
            
        db.session.delete(flashcard)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados', methods=['POST'])
@jwt_required()
def criar_simulado():
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        simulado = Simulado(
            nome=data['nome'],
            descricao=data['descricao'],
            user_id=user_id
        )
        
        db.session.add(simulado)
        db.session.commit()
        
        return jsonify({'message': 'Simulado criado com sucesso'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados', methods=['GET'])
@jwt_required()
def listar_simulados():
    try:
        user_id = int(get_jwt_identity())
        simulados = Simulado.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            'id': s.id,
            'nome': s.nome,
            'descricao': s.descricao,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
            'user_id': s.user_id
        } for s in simulados]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados/questoes/<int:id>', methods=['GET'])
@jwt_required()
def get_simulado_questoes(id):
    try:
        simulado = Simulado.query.get(id)
        if not simulado:
            return jsonify({'error': 'Simulado não encontrado'}), 404
            
        questoes = db.session.query(Questao).join(SimuladoQuestao).filter(
            SimuladoQuestao.simulado_id == id
        ).all()
        
        return jsonify({
            'id': simulado.id,
            'nome': simulado.nome,
            'descricao': simulado.descricao,
            'created_at': simulado.created_at.isoformat(),
            'updated_at': simulado.updated_at.isoformat(),
            'user_id': simulado.user_id,
            'questoes': [{
                'id': q.id,
                'pergunta': q.pergunta,
                'correta': q.correta,
                'created_at': q.created_at.isoformat(),
                'updated_at': q.updated_at.isoformat()
            } for q in questoes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados/<int:id>', methods=['PUT'])
@jwt_required()
def update_simulado(id):
    try:
        simulado = Simulado.query.get(id)
        if not simulado:
            return jsonify({'error': 'Simulado não encontrado'}), 404
            
        data = request.get_json()
        
        if 'nome' in data:
            simulado.nome = data['nome']
        if 'descricao' in data:
            simulado.descricao = data['descricao']
            
        db.session.commit()
        
        return jsonify({'message': 'Simulado atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_simulado(id):
    try:
        simulado = Simulado.query.get(id)
        if not simulado:
            return jsonify({'error': 'Simulado não encontrado'}), 404
            
        db.session.delete(simulado)
        db.session.commit()
        
        return jsonify({'message': 'Simulado deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questoes', methods=['POST'])
@jwt_required()
def criar_questao():
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        questao = Questao(
            pergunta=data['pergunta'],
            correta=data['correta'],
            tipo=data['tipo'],
            publica=data.get('publica', False),
            user_id=user_id
        )
        
        db.session.add(questao)
        db.session.commit()
        
        return jsonify({'message': 'Questão criada com sucesso'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questoes', methods=['GET'])
@jwt_required()
def listar_questoes():
    try:
        user_id = int(get_jwt_identity())
        questoes = Questao.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            'id': q.id,
            'pergunta': q.pergunta,
            'correta': q.correta,
            'tipo': q.tipo,
            'publica': q.publica,
            'created_at': q.created_at.isoformat(),
            'updated_at': q.updated_at.isoformat(),
            'user_id': q.user_id
        } for q in questoes]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questoes/<int:id>', methods=['PUT'])
@jwt_required()
def update_questao(id):
    try:
        questao = Questao.query.get(id)
        if not questao:
            return jsonify({'error': 'Questão não encontrada'}), 404
            
        data = request.get_json()
        
        if 'pergunta' in data:
            questao.pergunta = data['pergunta']
        if 'correta' in data:
            questao.correta = data['correta']
        if 'tipo' in data:
            questao.tipo = data['tipo']
        if 'publica' in data:
            questao.publica = data['publica']
            
        db.session.commit()
        
        return jsonify({'message': 'Questão atualizada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questoes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_questao(id):
    try:
        questao = Questao.query.get(id)
        if not questao:
            return jsonify({'error': 'Questão não encontrada'}), 404
            
        db.session.delete(questao)
        db.session.commit()
        
        return jsonify({'message': 'Questão deletada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questoes/publicas', methods=['GET'])
@jwt_required()
def listar_questoes_publicas():
    try:
        questoes = db.session.query(Questao, Usuario.apelido).join(
            Usuario, Questao.user_id == Usuario.id
        ).filter(Questao.publica == True).all()
        
        categoria = request.args.get('categoria')
        if categoria:
            questoes = [(q, apelido) for q, apelido in questoes if q.tipo == categoria]
        
        return jsonify([{
            'id': q.id,
            'pergunta': q.pergunta,
            'correta': q.correta,
            'tipo': q.tipo,
            'publica': q.publica,
            'created_at': q.created_at.isoformat(),
            'user_id': q.user_id,
            'apelido': apelido
        } for q, apelido in questoes]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users', methods=['GET'])
@jwt_required()
def listar_usuarios():
    try:
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        
        if not usuario or not usuario.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
            
        usuarios = Usuario.query.all()
        
        return jsonify([{
            'id': u.id,
            'nomeCompleto': u.nome_completo,
            'apelido': u.apelido,
            'dataNascimento': u.data_nascimento.isoformat(),
            'escolaridade': u.escolaridade,
            'email': u.email,
            'aceitouTermos': u.aceitou_termos,
            'is_admin': u.is_admin,
            'created_at': u.created_at.isoformat()
        } for u in usuarios]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    try:
        current_user_id = int(get_jwt_identity())
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
            
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        data = request.get_json()
        
        if 'apelido' in data:
            usuario.apelido = data['apelido']
        if 'escolaridade' in data:
            usuario.escolaridade = data['escolaridade']
        if 'nome_completo' in data:
            usuario.nome_completo = data['nome_completo']
        if 'is_admin' in data:
            usuario.is_admin = data['is_admin']
            
        db.session.commit()
        
        return jsonify({'message': 'Usuário atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    try:
        current_user_id = int(get_jwt_identity())
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
            
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/estatisticas', methods=['GET'])
@jwt_required()
def get_estatisticas():
    try:
        user_id = int(get_jwt_identity())
        
        conteudos_count = Conteudo.query.filter_by(user_id=user_id).count()
        flashcards_count = Flashcard.query.filter_by(user_id=user_id).count()
        simulados_count = Simulado.query.filter_by(user_id=user_id).count()
        questoes_count = Questao.query.filter_by(user_id=user_id).count()
        
        usuario = Usuario.query.get(user_id)
        total_usuarios = 0
        total_conteudos = 0
        
        if usuario and usuario.is_admin:
            total_usuarios = Usuario.query.count()
            total_conteudos = Conteudo.query.count()
        
        return jsonify({
            'usuario': {
                'conteudos': conteudos_count,
                'flashcards': flashcards_count,
                'simulados': simulados_count,
                'questoes': questoes_count
            },
            'geral': {
                'usuarios': total_usuarios,
                'conteudos': total_conteudos
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados/<int:id>/adicionar-questao', methods=['POST'])
@jwt_required()
def adicionar_questao_simulado(id):
    try:
        data = request.get_json()
        questao_id = data['questao_id']
        
        simulado = Simulado.query.get(id)
        if not simulado:
            return jsonify({'error': 'Simulado não encontrado'}), 404
        
        questao = Questao.query.get(questao_id)
        if not questao:
            return jsonify({'error': 'Questão não encontrada'}), 404
        
        relacao = SimuladoQuestao.query.filter_by(
            simulado_id=id, 
            questao_id=questao_id
        ).first()
        
        if relacao:
            return jsonify({'error': 'Questão já adicionada ao simulado'}), 400
        
        nova_relacao = SimuladoQuestao(
            simulado_id=id,
            questao_id=questao_id
        )
        
        db.session.add(nova_relacao)
        db.session.commit()
        
        return jsonify({'message': 'Questão adicionada ao simulado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/simulados/<int:id>/remover-questao', methods=['DELETE'])
@jwt_required()
def remover_questao_simulado(id):
    try:
        data = request.get_json()
        questao_id = data['questao_id']
        
        relacao = SimuladoQuestao.query.filter_by(
            simulado_id=id,
            questao_id=questao_id
        ).first()
        
        if not relacao:
            return jsonify({'error': 'Questão não encontrada no simulado'}), 404
        
        db.session.delete(relacao)
        db.session.commit()
        
        return jsonify({'message': 'Questão removida do simulado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        try:
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(questao)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'tipo' not in columns:
                db.session.execute(text("ALTER TABLE questao ADD COLUMN tipo VARCHAR(50)"))
            
            if 'publica' not in columns:
                db.session.execute(text("ALTER TABLE questao ADD COLUMN publica BOOLEAN DEFAULT 0"))
            
            db.session.commit()
        except Exception as e:
            pass
        
        admin = Usuario.query.filter_by(email='admin@enempro.com').first()
        if not admin:
            admin = Usuario(
                nome_completo='Administrador ENEMPRO',
                apelido='Admin',
                data_nascimento=datetime(1990, 1, 1).date(),
                escolaridade='Superior',
                email='admin@enempro.com',
                telefone='(84) 99999-9999',
                senha=generate_password_hash('admin123'),
                aceitou_termos=True,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
