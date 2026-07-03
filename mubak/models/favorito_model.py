from database import get_db_connection
from datetime import date


def get_favoritos_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT f.*, p.nome, p.preco, p.estoque, p.status_prod,
                  (SELECT imagem FROM imagem_produto WHERE id_produto=p.id_produto LIMIT 1) AS imagem
           FROM favorito f
           JOIN produto p ON f.id_produto = p.id_produto
           WHERE f.id_usuario=?
           ORDER BY f.data_criacao DESC, f.id_favorito DESC""",
        (id_usuario,)
    ).fetchall()
    conn.close()
    return rows


def get_ids_favoritos_usuario(id_usuario):
    """Retorna um conjunto (set) com os ids de produto favoritados pelo usuário.
    Útil para marcar o ícone de coração nas grades de produtos sem 1 query por item."""
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT id_produto FROM favorito WHERE id_usuario=?', (id_usuario,)
    ).fetchall()
    conn.close()
    return {row['id_produto'] for row in rows}


def is_favorito(id_usuario, id_produto):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT 1 FROM favorito WHERE id_usuario=? AND id_produto=?',
        (id_usuario, id_produto)
    ).fetchone()
    conn.close()
    return row is not None


def adicionar_favorito(id_usuario, id_produto):
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO favorito (id_usuario, id_produto, data_criacao) VALUES (?,?,?)',
        (id_usuario, id_produto, date.today().isoformat())
    )
    conn.commit()
    conn.close()


def remover_favorito(id_usuario, id_produto):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM favorito WHERE id_usuario=? AND id_produto=?',
        (id_usuario, id_produto)
    )
    conn.commit()
    conn.close()


def toggle_favorito(id_usuario, id_produto):
    """Alterna o estado de favorito do produto para o usuário.
    Retorna True se foi adicionado, False se foi removido."""
    if is_favorito(id_usuario, id_produto):
        remover_favorito(id_usuario, id_produto)
        return False
    adicionar_favorito(id_usuario, id_produto)
    return True


def contar_favoritos(id_usuario):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT COUNT(*) AS total FROM favorito WHERE id_usuario=?', (id_usuario,)
    ).fetchone()
    conn.close()
    return row['total'] if row else 0
