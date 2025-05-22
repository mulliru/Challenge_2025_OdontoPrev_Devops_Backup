import requests
from faker import Faker
import random

# URL base da API
BASE_URL = "http://127.0.0.1:8000"

# Inicializa Faker para gerar dados aleatórios
fake = Faker("pt_BR")

# Variáveis globais para armazenar IDs criados
cliente_id = None
profissional_id = None
atendimento_id = None
pagamento_id = None
sinistro_id = None

#  Teste: Criar um cliente
def test_criar_cliente():
    global cliente_id
    
    ddd = random.choice(["11", "21", "31", "41", "61", "71", "51", "48"])
    numero = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    telefone = f"({ddd}) {numero}"
    
    nome_completo = fake.name()
    nome_email = nome_completo.lower().replace(" ", ".").replace("dr.", "").replace("dra.", "").strip()
    email = f"{nome_email}@cliente.com"
    
    cliente_exemplo = {
        "nome": nome_completo,
        "email": email,
        "cpf": fake.cpf().replace(".", "").replace("-", ""),  # CPF único
        "telefone": telefone
    }
    resposta = requests.post(f"{BASE_URL}/clientes", json=cliente_exemplo)
    
    assert resposta.status_code in [201, 400]  # Permite 400 se já existir
    if resposta.status_code == 201:
        cliente_id = resposta.json().get("id")

#  Teste: Listar clientes
def test_listar_clientes():
    """Testa a listagem de clientes."""
    resposta = requests.get(f"{BASE_URL}/clientes")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)

#  Teste: Criar um profissional
def test_criar_profissional():
    global profissional_id
    
    especialidades_odonto = [
        "Ortodontia", "Endodontia", "Clínico Geral",
        "Implantodontia", "Periodontia", "Odontopediatria",
        "Estomatologia", "Radiologia Odontológica"
    ]
    
    ddd = random.choice(["11", "21", "31", "41", "61", "71", "51", "48"])
    numero = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    telefone = f"({ddd}) {numero}"
    
    nome_completo = fake.name()
    nome_email = nome_completo.lower().replace(" ", ".").replace("dr.", "").replace("dra.", "").strip()
    email = f"{nome_email}@odontoprev.com.br"

    profissional_exemplo = {
        "nome": nome_completo,
        "email": email,
        "cpf": fake.cpf().replace(".", "").replace("-", ""),  # CPF limpo
        "cro": f"CRO{fake.random_int(min=10000, max=99999)}",
        "especialidade": random.choice(especialidades_odonto),
        "telefone": telefone
    }

    resposta = requests.post(f"{BASE_URL}/profissionais", json=profissional_exemplo)

    assert resposta.status_code == 201
    profissional_id = resposta.json().get("id")

#  Teste: Listar profissionais
def test_listar_profissionais():
    """Testa a listagem de profissionais."""
    resposta = requests.get(f"{BASE_URL}/profissionais")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)

#  Teste: Criar um atendimento
def test_criar_atendimento():
    """Testa a criação de um atendimento."""
    global atendimento_id
    atendimento_exemplo = {
        "cliente_id": cliente_id or 1,
        "profissional_id": profissional_id or 1,
        "descricao": "Consulta geral"
    }
    resposta = requests.post(f"{BASE_URL}/atendimentos", json=atendimento_exemplo)
    assert resposta.status_code == 201
    atendimento_id = resposta.json().get("id")

#  Teste: Listar atendimentos
def test_listar_atendimentos():
    """Testa a listagem de atendimentos."""
    resposta = requests.get(f"{BASE_URL}/atendimentos")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)

#  Teste: Criar um pagamento
def test_criar_pagamento():
    """Testa a criação de um pagamento."""
    global pagamento_id
    pagamento_exemplo = {
        "atendimento_id": atendimento_id or 1,
        "valor": 200.00,
        "metodo_pagamento": "PIX",
        "status": "Pendente"
    }
    resposta = requests.post(f"{BASE_URL}/pagamentos", json=pagamento_exemplo)
    assert resposta.status_code == 201
    pagamento_id = resposta.json().get("id")

#  Teste: Listar pagamentos
def test_listar_pagamentos():
    """Testa a listagem de pagamentos."""
    resposta = requests.get(f"{BASE_URL}/pagamentos")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)

#  Teste: Criar um sinistro
def test_criar_sinistro():
    """Testa a criação de um sinistro."""
    global sinistro_id
    sinistro_exemplo = {
        "atendimento_id": atendimento_id or 1,
        "tipo_sinistro": "Cobrança Indevida",
        "descricao": "Paciente recebeu cobrança duplicada",
        "status": "Em análise"
    }
    resposta = requests.post(f"{BASE_URL}/sinistros", json=sinistro_exemplo)
    assert resposta.status_code == 201
    sinistro_id = resposta.json().get("id")

#  Teste: Listar sinistros
def test_listar_sinistros():
    """Testa a listagem de sinistros."""
    resposta = requests.get(f"{BASE_URL}/sinistros")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)

#  Teste: Atualizar cliente
def test_atualizar_cliente():
    """Testa a atualização de um cliente existente."""
    if cliente_id:
        # Primeiro, recupera os dados atuais do cliente
        resposta_get = requests.get(f"{BASE_URL}/clientes/{cliente_id}")
        assert resposta_get.status_code == 200
        cliente_original = resposta_get.json()

        cliente_atualizado = {
            "nome": "Cliente Atualizado",
            "email": "cliente.atualizado@example.com",
            "cpf": cliente_original.get("cpf"),  # mantém o mesmo CPF
            "telefone": "(11) 91111-2222"
        }

        resposta = requests.put(f"{BASE_URL}/clientes/{cliente_id}", json=cliente_atualizado)
        assert resposta.status_code == 200

#  Teste: Excluir cliente
def test_deletar_cliente():
    novo_cliente = {
        "nome": "Cliente Temp",
        "email": "temp@teste.com",
        "cpf": "99999999999",  # CPF fixo para cliente temporário
        "telefone": "11999999999"
    }

    # POST - cria o cliente
    res_post = requests.post(f"{BASE_URL}/clientes", json=novo_cliente)
    assert res_post.status_code in [201, 400]

    if res_post.status_code == 201:
        cliente_temp_id = res_post.json()["id"]

        # DELETE - deleta o cliente recém-criado
        res_delete = requests.delete(f"{BASE_URL}/clientes/{cliente_temp_id}")
        assert res_delete.status_code == 200
        assert res_delete.json()["message"] == "Cliente deletado com sucesso"



#  Teste: Atualizar profissional
def test_atualizar_profissional():
    """Testa a atualização de um profissional existente."""
    if profissional_id:
        profissional_atualizado = {
            "nome": "Dr. Atualizado",
            "email": "dr.atualizado@example.com",
            "cpf": "98765432100",
            "cro": "SP-123456",
            "especialidade": "Ortopedia",
            "telefone": "(11) 92222-3333"
        }
        resposta = requests.put(f"{BASE_URL}/profissionais/{profissional_id}", json=profissional_atualizado)
        assert resposta.status_code == 200

#  Teste: Excluir profissional
def test_deletar_profissional():
    """Testa a exclusão de um profissional."""
    if profissional_id:
        resposta = requests.delete(f"{BASE_URL}/profissionais/{profissional_id}")
        assert resposta.status_code == 200
