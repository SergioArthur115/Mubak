from database import get_db_connection


# ── Usuário ────────────────────────────────────────────────────────────────────

def criar_usuario(nome, email, senha, telefone, cpf, data_nasc, foto, id_perfil=2):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO usuario (nome, email, senha, telefone, cpf, data_nasc, foto, id_perfil)
           VALUES (?,?,?,?,?,?,?,?)""",
        (nome, email, senha, telefone, cpf, data_nasc, foto, id_perfil)
    )
    conn.commit()
    conn.close()


def get_usuario_por_email(email):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM usuario WHERE email=?', (email,)
    ).fetchone()
    conn.close()
    return user


def get_usuario_por_id(id_usuario):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM usuario WHERE id_usuario=?', (id_usuario,)
    ).fetchone()
    conn.close()
    return user


def get_todos_usuarios():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuario').fetchall()
    conn.close()
    return users


def buscar_usuarios(nome=None, email=None):
    """Consulta administrativa de usuários por nome e/ou e-mail (busca parcial)."""
    conn = get_db_connection()
    query = 'SELECT * FROM usuario WHERE 1=1'
    params = []
    if nome:
        query += ' AND nome LIKE ?'
        params.append(f'%{nome}%')
    if email:
        query += ' AND email LIKE ?'
        params.append(f'%{email}%')
    users = conn.execute(query, params).fetchall()
    conn.close()
    return users


def atualizar_usuario(id_usuario, nome, email, telefone, foto):
    conn = get_db_connection()
    conn.execute(
        'UPDATE usuario SET nome=?, email=?, telefone=?, foto=? WHERE id_usuario=?',
        (nome, email, telefone, foto, id_usuario)
    )
    conn.commit()
    conn.close()


def atualizar_usuario_admin(id_usuario, nome, email, telefone, foto, id_perfil):
    """Atualização administrativa, incluindo o perfil (Admin/Usuário)."""
    conn = get_db_connection()
    conn.execute(
        'UPDATE usuario SET nome=?, email=?, telefone=?, foto=?, id_perfil=? WHERE id_usuario=?',
        (nome, email, telefone, foto, id_perfil, id_usuario)
    )
    conn.commit()
    conn.close()


def deletar_usuario(id_usuario):
    conn = get_db_connection()
    conn.execute('DELETE FROM usuario WHERE id_usuario=?', (id_usuario,))
    conn.commit()
    conn.close()


def is_admin(id_usuario):
    user = get_usuario_por_id(id_usuario)
    return user and user['id_perfil'] == 1


# ── Endereço ──────────────────────────────────────────────────────────────────

def get_enderecos_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM endereco WHERE id_usuario=?', (id_usuario,)
    ).fetchall()
    conn.close()
    return rows


def criar_endereco(id_usuario, cep, bairro, cidade, estado, complemento, numero, principal=False):
    conn = get_db_connection()
    if principal:
        conn.execute(
            'UPDATE endereco SET principal=0 WHERE id_usuario=?', (id_usuario,)
        )
    conn.execute(
        """INSERT INTO endereco (cep, bairro, cidade, estado, complemento, numero, principal, id_usuario)
           VALUES (?,?,?,?,?,?,?,?)""",
        (cep, bairro, cidade, estado, complemento, numero, int(principal), id_usuario)
    )
    conn.commit()
    conn.close()
