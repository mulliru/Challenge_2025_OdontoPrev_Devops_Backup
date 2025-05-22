import pyodbc
from flask import Flask, request, jsonify
import traceback
import os
from config import DB_CONFIG

app = Flask(__name__)  # Agora sim!


# Função para conectar ao banco
def connect_db():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

# Funções auxiliares
def buscar_por_id(tabela, id, campos):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f"SELECT {', '.join(campos)} FROM {tabela} WHERE id = ?"
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify(dict(zip(campos, row))), 200
        else:
            return resposta_erro(f"{tabela.capitalize()} não encontrado", 404)
    except Exception as e:
        return resposta_erro(str(e), 500)
    
# Função para retornar sucesso
def resposta_sucesso(message, data=None, status_code=200):
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

## Função para retornar erro
def resposta_erro(error_message, status_code=400):
    return jsonify({"status": "error", "message": error_message}), status_code

#  Endpoint de Teste
@app.route('/')
def home():
    return "API Flask está rodando!"

#  CRUD - Clientes
@app.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.get_json()
    nome = data.get("nome")
    email = data.get("email")
    cpf = data.get("cpf")
    telefone = data.get("telefone")

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, email, cpf, telefone)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
        """, (nome, email, cpf, telefone))
        cliente_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({"message": "Cliente criado com sucesso!", "id": cliente_id}), 201
    except Exception as e:
        traceback.print_exc()
        print(f"Erro ao criar cliente: {e}")
        return jsonify({"error": str(e)}), 500

# Método para listar clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, cpf, telefone FROM clientes")
        clientes = [{"id": row[0], "nome": row[1], "email": row[2], "cpf": row[3], "telefone": row[4]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(clientes)
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/clientes/<int:id>', methods=['GET'])
def buscar_cliente(id):
    campos = ["id", "nome", "email", "cpf", "telefone"]
    return buscar_por_id("clientes", id, campos)


#Método para atualizar cliente
@app.route('/clientes/<int:id>', methods=['PUT'])
def atualizar_cliente(id):
    data = request.get_json()
    nome = data.get("nome")
    email = data.get("email")
    cpf = data.get("cpf")
    telefone = data.get("telefone")
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Cliente não encontrado", 404)
        cursor.execute(
            "UPDATE clientes SET nome = ?, email = ?, cpf = ?, telefone = ? WHERE id = ?",
            (nome, email, cpf, telefone, id)
        )
        conn.commit()
        conn.close()
        return resposta_sucesso("Cliente atualizado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Cliente não encontrado", 404)
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return resposta_sucesso("Cliente deletado com sucesso")
    except pyodbc.IntegrityError:
        return resposta_erro("Não é possível deletar cliente com atendimentos vinculados", 400)
    except Exception as e:
        return resposta_erro(str(e), 500)

############################################################################################################################################################################
#  CRUD - Profissionais
@app.route('/profissionais', methods=['POST'])
def criar_profissional():
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO profissionais (nome, email, cpf, cro, especialidade, telefone)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data["nome"], data["email"], data["cpf"], data["cro"], data["especialidade"], data["telefone"])
        )
        profissional_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return resposta_sucesso("Profissional criado com sucesso!", {"id": profissional_id}, 201)
    except Exception as e:
        return resposta_erro(str(e), 500)


@app.route('/profissionais', methods=['GET'])
def listar_profissionais():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, cpf, cro, especialidade, telefone FROM profissionais")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([
            dict(zip(["id", "nome", "email", "cpf", "cro", "especialidade", "telefone"], row))
            for row in rows
        ])
    except Exception as e:
        return resposta_erro(str(e), 500)
    
@app.route('/profissionais/<int:id>', methods=['GET'])
def buscar_profissional(id):
    return buscar_por_id(
        "profissionais",
        id,
        ["id", "nome", "email", "cpf", "cro", "especialidade", "telefone"]
    )
    
@app.route('/profissionais/<int:id>', methods=['PUT'])
def atualizar_profissional(id):
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM profissionais WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Profissional não encontrado", 404)

        cursor.execute("""
            UPDATE profissionais
            SET nome = ?, email = ?, cpf = ?, cro = ?, especialidade = ?, telefone = ?
            WHERE id = ?
        """, (data["nome"], data["email"], data["cpf"], data["cro"], data["especialidade"], data["telefone"], id))

        conn.commit()
        conn.close()
        return resposta_sucesso("Profissional atualizado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/profissionais/<int:id>', methods=['DELETE'])
def deletar_profissional(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM profissionais WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Profissional não encontrado", 404)

        cursor.execute("DELETE FROM profissionais WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return resposta_sucesso("Profissional deletado com sucesso")
    except pyodbc.IntegrityError:
        return resposta_erro("Não é possível deletar profissional com atendimentos vinculados", 400)
    except Exception as e:
        return resposta_erro(str(e), 500)

############################################################################################################################################################################
#  CRUD - Atendimentos
@app.route('/atendimentos', methods=['POST'])
def criar_atendimento():
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO atendimentos (cliente_id, profissional_id, descricao, status)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            (data["cliente_id"], data["profissional_id"], data["descricao"], data.get("status", "Pendente"))
        )
        atendimento_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return resposta_sucesso("Atendimento registrado com sucesso!", {"id": atendimento_id}, 201)
    except Exception as e:
        return resposta_erro(str(e), 500)


@app.route('/atendimentos', methods=['GET'])
def listar_atendimentos():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_id, profissional_id, data_atendimento, descricao, status FROM atendimentos")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([
            dict(zip(["id", "cliente_id", "profissional_id", "data_atendimento", "descricao", "status"], row))
            for row in rows
        ])
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/atendimentos/<int:id>', methods=['GET'])
def buscar_atendimento(id):
    return buscar_por_id(
        "atendimentos",
        id,
        ["id", "cliente_id", "profissional_id", "data_atendimento", "descricao", "status"]
    )
    
@app.route('/atendimentos/<int:id>', methods=['PUT'])
def atualizar_atendimento(id):
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM atendimentos WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Atendimento não encontrado", 404)

        cursor.execute("""
            UPDATE atendimentos
            SET cliente_id = ?, profissional_id = ?, descricao = ?, status = ?
            WHERE id = ?
        """, (data["cliente_id"], data["profissional_id"], data["descricao"], data["status"], id))

        conn.commit()
        conn.close()
        return resposta_sucesso("Atendimento atualizado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)


@app.route('/atendimentos/<int:id>', methods=['DELETE'])
def deletar_atendimento(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM atendimentos WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Atendimento não encontrado", 404)

        cursor.execute("DELETE FROM atendimentos WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return resposta_sucesso("Atendimento deletado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)
    
############################################################################################################################################################################
#  CRUD - Pagamentos
@app.route('/pagamentos', methods=['POST'])
def criar_pagamento():
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO pagamentos (atendimento_id, valor, metodo_pagamento, status)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            (data["atendimento_id"], data["valor"], data["metodo_pagamento"], data.get("status", "Pendente"))
        )
        pagamento_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return resposta_sucesso("Pagamento registrado com sucesso!", {"id": pagamento_id}, 201)
    except Exception as e:
        return resposta_erro(str(e), 500)


@app.route('/pagamentos', methods=['GET'])
def listar_pagamentos():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, atendimento_id, valor, metodo_pagamento, data_pagamento, status FROM pagamentos")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([
            dict(zip(["id", "atendimento_id", "valor", "metodo_pagamento", "data_pagamento", "status"], row))
            for row in rows
        ])
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/pagamentos/<int:id>', methods=['GET'])
def buscar_pagamento(id):
    return buscar_por_id(
        "pagamentos",
        id,
        ["id", "atendimento_id", "valor", "metodo_pagamento", "data_pagamento", "status"]
    )
    
@app.route('/pagamentos/<int:id>', methods=['PUT'])
def atualizar_pagamento(id):
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM pagamentos WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Pagamento não encontrado", 404)

        cursor.execute("""
            UPDATE pagamentos
            SET atendimento_id = ?, valor = ?, metodo_pagamento = ?, status = ?
            WHERE id = ?
        """, (data["atendimento_id"], data["valor"], data["metodo_pagamento"], data["status"], id))

        conn.commit()
        conn.close()
        return resposta_sucesso("Pagamento atualizado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)


@app.route('/pagamentos/<int:id>', methods=['DELETE'])
def deletar_pagamento(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM pagamentos WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Pagamento não encontrado", 404)

        cursor.execute("DELETE FROM pagamentos WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return resposta_sucesso("Pagamento deletado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)
    
################################################################################################################################################################################

#CRUD - Sinistros
@app.route('/sinistros', methods=['POST'])
def criar_sinistro():
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sinistros (atendimento_id, tipo_sinistro, descricao, status)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            (data["atendimento_id"], data["tipo_sinistro"], data["descricao"], data.get("status", "Em análise"))
        )
        sinistro_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return resposta_sucesso("Sinistro registrado com sucesso!", {"id": sinistro_id}, 201)
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/sinistros', methods=['GET'])
def listar_sinistros():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, atendimento_id, tipo_sinistro, descricao, data_registro, status FROM sinistros")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([
            dict(zip(["id", "atendimento_id", "tipo_sinistro", "descricao", "data_registro", "status"], row))
            for row in rows
        ])
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/sinistros/<int:id>', methods=['GET'])
def buscar_sinistro(id):
    return buscar_por_id(
        "sinistros",
        id,
        ["id", "atendimento_id", "tipo_sinistro", "descricao", "data_registro", "status"]
    )

@app.route('/sinistros/<int:id>', methods=['PUT'])
def atualizar_sinistro(id):
    data = request.get_json()
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM sinistros WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Sinistro não encontrado", 404)

        cursor.execute("""
            UPDATE sinistros
            SET atendimento_id = ?, tipo_sinistro = ?, descricao = ?, status = ?
            WHERE id = ?
        """, (data["atendimento_id"], data["tipo_sinistro"], data["descricao"], data["status"], id))

        conn.commit()
        conn.close()
        return resposta_sucesso("Sinistro atualizado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)

@app.route('/sinistros/<int:id>', methods=['DELETE'])
def deletar_sinistro(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM sinistros WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            return resposta_erro("Sinistro não encontrado", 404)

        cursor.execute("DELETE FROM sinistros WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return resposta_sucesso("Sinistro deletado com sucesso")
    except Exception as e:
        return resposta_erro(str(e), 500)

################################################################################################################################################################################

if __name__ == '__main__':
    print("🚀 API rodando em: http://0.0.0.0:8000/")
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.run(host="0.0.0.0", port=8000, debug=True)
