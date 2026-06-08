import sqlite3
import hashlib

BANCO = "fototerma.db"

# ── Inicialização ─────────────────────────────────────────────────────────────

def criar_tabelas():
    """Cria as tabelas do banco se ainda não existirem."""
    with sqlite3.connect(BANCO) as con:

        # Tabela de atendimentos
        con.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nome          TEXT    NOT NULL,
                endereco      TEXT    NOT NULL,
                consumo       REAL    NOT NULL,
                tarifa        REAL    NOT NULL,
                area_disp     REAL    NOT NULL,
                sombra        REAL    NOT NULL,
                potencia_placa REAL   NOT NULL,
                largura_placa REAL    NOT NULL,
                altura_placa  REAL    NOT NULL,
                ponto_labren  INTEGER NOT NULL,
                irradiacao    REAL    NOT NULL,
                num_paineis   INTEGER NOT NULL,
                area_nec      REAL    NOT NULL,
                investimento  REAL    NOT NULL,
                payback       REAL    NOT NULL,
                roi           REAL    NOT NULL,
                lucro_liquido REAL    NOT NULL,
                status        TEXT    NOT NULL,
                data          TEXT    DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # Tabela de usuários
        con.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT    NOT NULL,
                email     TEXT    NOT NULL UNIQUE,
                senha     TEXT    NOT NULL,
                perfil    TEXT    NOT NULL CHECK(perfil IN ('consultor', 'cliente')),
                registro  TEXT,
                endereco  TEXT,
                regiao    INTEGER,
                data      TEXT    DEFAULT (datetime('now', 'localtime'))
            )
        """)

# ── Utilitário ────────────────────────────────────────────────────────────────

def _hash_senha(senha):
    """Gera hash SHA-256 da senha. Nunca salva senha em texto puro."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

# ── CRUD Atendimentos ─────────────────────────────────────────────────────────

def salvar_atendimento(dados):
    """Insere um novo atendimento. Retorna o id gerado."""
    with sqlite3.connect(BANCO) as con:
        cursor = con.execute("""
            INSERT INTO atendimentos (
                nome, endereco, consumo, tarifa, area_disp, sombra,
                potencia_placa, largura_placa, altura_placa,
                ponto_labren, irradiacao, num_paineis, area_nec,
                investimento, payback, roi, lucro_liquido, status
            ) VALUES (
                :nome, :endereco, :consumo, :tarifa, :area_disp, :sombra,
                :potencia_placa, :largura_placa, :altura_placa,
                :ponto_labren, :irradiacao, :num_paineis, :area_nec,
                :investimento, :payback, :roi, :lucro_liquido, :status
            )
        """, dados)
        return cursor.lastrowid

def listar_atendimentos():
    """Retorna todos os atendimentos do mais recente ao mais antigo."""
    with sqlite3.connect(BANCO) as con:
        con.row_factory = sqlite3.Row
        return con.execute("""
            SELECT * FROM atendimentos ORDER BY data DESC
        """).fetchall()

def buscar_atendimento(id):
    """Retorna um atendimento pelo ID."""
    with sqlite3.connect(BANCO) as con:
        con.row_factory = sqlite3.Row
        return con.execute("""
            SELECT * FROM atendimentos WHERE id = ?
        """, (id,)).fetchone()

def atualizar_atendimento(id, dados):
    """Atualiza os campos de um atendimento existente."""
    with sqlite3.connect(BANCO) as con:
        con.execute("""
            UPDATE atendimentos SET
                nome           = :nome,
                endereco       = :endereco,
                consumo        = :consumo,
                tarifa         = :tarifa,
                area_disp      = :area_disp,
                sombra         = :sombra,
                potencia_placa = :potencia_placa,
                largura_placa  = :largura_placa,
                altura_placa   = :altura_placa,
                ponto_labren   = :ponto_labren,
                irradiacao     = :irradiacao,
                num_paineis    = :num_paineis,
                area_nec       = :area_nec,
                investimento   = :investimento,
                payback        = :payback,
                roi            = :roi,
                lucro_liquido  = :lucro_liquido,
                status         = :status
            WHERE id = :id
        """, {**dados, 'id': id})

def deletar_atendimento(id):
    """Remove um atendimento pelo ID."""
    with sqlite3.connect(BANCO) as con:
        con.execute("DELETE FROM atendimentos WHERE id = ?", (id,))

# ── CRUD Usuários ─────────────────────────────────────────────────────────────

def cadastrar_usuario(dados):
    """
    Insere um novo usuário. Retorna o id gerado ou None se o email já existir.
    'dados' deve conter: nome, email, senha, perfil
    Campos opcionais: registro (consultor), endereco e regiao (cliente)
    """
    try:
        with sqlite3.connect(BANCO) as con:
            cursor = con.execute("""
                INSERT INTO usuarios (nome, email, senha, perfil, registro, endereco, regiao)
                VALUES (:nome, :email, :senha, :perfil, :registro, :endereco, :regiao)
            """, {
                'nome'    : dados['nome'],
                'email'   : dados['email'],
                'senha'   : _hash_senha(dados['senha']),
                'perfil'  : dados['perfil'],
                'registro': dados.get('registro'),
                'endereco': dados.get('endereco'),
                'regiao'  : dados.get('regiao'),
            })
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Email já cadastrado
        return None

def verificar_login(email, senha, perfil):
    """
    Verifica se o email, senha e perfil batem com um usuário cadastrado.
    Retorna o usuário (Row) se correto, ou None se inválido.
    """
    with sqlite3.connect(BANCO) as con:
        con.row_factory = sqlite3.Row
        return con.execute("""
            SELECT * FROM usuarios
            WHERE email = ? AND senha = ? AND perfil = ?
        """, (email, _hash_senha(senha), perfil)).fetchone()

def buscar_usuario_por_email(email):
    """Retorna um usuário pelo email."""
    with sqlite3.connect(BANCO) as con:
        con.row_factory = sqlite3.Row
        return con.execute("""
            SELECT * FROM usuarios WHERE email = ?
        """, (email,)).fetchone()

def listar_usuarios():
    """Retorna todos os usuários cadastrados."""
    with sqlite3.connect(BANCO) as con:
        con.row_factory = sqlite3.Row
        return con.execute("""
            SELECT id, nome, email, perfil, data FROM usuarios ORDER BY data DESC
        """).fetchall()

def deletar_usuario(id):
    """Remove um usuário pelo ID."""
    with sqlite3.connect(BANCO) as con:
        con.execute("DELETE FROM usuarios WHERE id = ?", (id,))

# ── Inicializa o banco ao importar o módulo ───────────────────────────────────
criar_tabelas()
