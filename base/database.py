import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("leituras.db")


class Usuario:
    def __init__(self, linha):
        self.id = linha["id"]
        self.nome = linha["nome"]
        self.email = linha["email"]
        self.senha_hash = linha["senha_hash"]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_activate(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS leituras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                paginas INTEGER NOT NULL,
                concluida INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )

        total = conexao.execute("SELECT COUNT(*) FROM leituras").fetchone()[0]
        if total == 0:
            conexao.executemany(
                """
                INSERT INTO leituras (titulo, autor, paginas, concluida)
                VALUES (?, ?, ?, ?)
                """,
                [
                    ("A Cartomante", "Machado de Assis", 18, 1),
                    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", 96, 0),
                    ("Capitães da Areia", "Jorge Amado", 280, 0),
                ],
            )


def montar_usuario(linha):
    if linha is None:
        return None
    return Usuario(linha)


def buscar_usuario_por_id(usuario_id):
    with conectar() as conexao:
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (usuario_id,),
        ).fetchone()
    return montar_usuario(linha)


def buscar_usuario_por_email(email):
    with conectar() as conexao:
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,),
        ).fetchone()
    return montar_usuario(linha)


def criar_usuario(nome, email, senha_hash):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
            """,
            (nome, email, senha_hash),
        )
    return buscar_usuario_por_id(cursor.lastrowid)


def listar_leituras(usuario_id):
    with conectar() as conexao:
        return conexao.execute(
            "SELECT * FROM leituras WHERE usuario_id = ? ORDER BY id DESC", 
            (usuario_id,)
        ).fetchall()


def buscar_leitura(leitura_id, usuario_id):
    with conectar() as conexao:
        return conexao.execute(
            "SELECT * FROM leituras WHERE id = ? AND usuario_id = ?",
            (leitura_id, usuario_id),
        ).fetchone()


def criar_leitura(usuario_id, titulo, autor, paginas):
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO leituras (usuario_id, titulo, autor, paginas)
            VALUES (?, ?, , ?)
            """,
            (usuario_id, titulo, autor, paginas),
        )


def atualizar_leitura(leitura_id, usuario_id, titulo, autor, paginas):
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE leituras
            SET titulo = ?, autor = ?, paginas = ?
            WHERE id = ? AND usuario_id
            """,
            (titulo, usuario_id, autor, paginas, leitura_id),
        )


def alternar_concluida(leitura_id, usuario_id):
    leitura = buscar_leitura(leitura_id, usuario_id)
    if leitura is None:
        return  

    novo_status = 0 if leitura["concluida"] else 1
    with conectar() as conexao:
        conexao.execute(
            "UPDATE leituras SET concluida = ? WHERE id = ? AND usuario_id = ?",
            (novo_status, leitura_id, usuario_id),
        )


def excluir_leitura(leitura_id, usuario_id):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM leituras WHERE id = ? AND usuario_id = ?",
            (leitura_id, usuario_id),
        )
