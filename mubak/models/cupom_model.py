from database import get_db_connection
from datetime import date


def get_todos_cupons():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM cupom ORDER BY id_cupom DESC").fetchall()
    conn.close()
    return rows


def get_cupom_por_id(id_cupom):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM cupom WHERE id_cupom=?", (id_cupom,)).fetchone()
    conn.close()
    return row


def get_cupom_por_codigo(codigo):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM cupom WHERE codigo=? COLLATE NOCASE", (codigo.strip(),)
    ).fetchone()
    conn.close()
    return row


def criar_cupom(codigo, inicio, fim, valor, ativo=True):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO cupom (codigo, inicio, fim, valor, ativo) VALUES (?,?,?,?,?)",
        (codigo.strip().upper(), inicio, fim, valor, int(bool(ativo))),
    )
    conn.commit()
    conn.close()


def atualizar_cupom(id_cupom, codigo, inicio, fim, valor, ativo):
    conn = get_db_connection()
    conn.execute(
        """UPDATE cupom
           SET codigo=?, inicio=?, fim=?, valor=?, ativo=?
           WHERE id_cupom=?""",
        (codigo.strip().upper(), inicio, fim, valor, int(bool(ativo)), id_cupom),
    )
    conn.commit()
    conn.close()


def alternar_status_cupom(id_cupom):
    """Alterna (ativa/desativa) o status de um cupom existente."""
    conn = get_db_connection()
    cupom = conn.execute(
        "SELECT ativo FROM cupom WHERE id_cupom=?", (id_cupom,)
    ).fetchone()
    if cupom:
        novo_status = 0 if cupom["ativo"] else 1
        conn.execute(
            "UPDATE cupom SET ativo=? WHERE id_cupom=?", (novo_status, id_cupom)
        )
        conn.commit()
    conn.close()


def deletar_cupom(id_cupom):
    conn = get_db_connection()
    conn.execute("DELETE FROM cupom WHERE id_cupom=?", (id_cupom,))
    conn.commit()
    conn.close()


def validar_cupom(codigo):
    """Retorna o cupom se ele existir, estiver ativo e dentro do período de validade.
    Caso contrário, retorna None."""
    if not codigo:
        return None

    cupom = get_cupom_por_codigo(codigo)
    if not cupom:
        return None
    if not cupom["ativo"]:
        return None

    hoje = date.today().isoformat()
    if cupom["inicio"] > hoje or cupom["fim"] < hoje:
        return None

    return cupom
