import pytest
import time
from painel_cliente import app, get_db, calculate_price, process_string

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            print("Inicializando o contexto do app e banco de dados.")
            get_db()
        yield client
        print("Fechando o contexto do app.")

@pytest.mark.timeout(10)
def test_calculate_price():
    print("Iniciando o teste de cálculo de preço com ['A', 'B'], 65.")
    total_price, discount, tax, final_price = calculate_price(['A', 'B'], 65)
    print(f"Resultado: Total: {total_price}, Desconto: {discount}, Imposto: {tax}, Preço final: {final_price}")
    assert total_price == 300
    assert discount == 30
    assert tax == 54
    assert final_price == 324

    print("Iniciando o teste de cálculo de preço com ['C', 'D'], 30.")
    total_price, discount, tax, final_price = calculate_price(['C', 'D'], 30)
    print(f"Resultado: Total: {total_price}, Desconto: {discount}, Imposto: {tax}, Preço final: {final_price}")
    assert total_price == 700
    assert discount == 0
    assert tax == 140
    assert final_price == 840

@pytest.mark.timeout(10)
def test_process_string():
    print("Iniciando o teste de processamento de string.")
    
    result = process_string("ABC")
    print(f"Processando 'ABC': {result}")
    assert result == "abc"
    
    result = process_string("abc")
    print(f"Processando 'abc': {result}")
    assert result == "ABC"
    
    result = process_string("AbC123")
    print(f"Processando 'AbC123': {result}")
    assert result == "aBc123"

@pytest.mark.timeout(10)
def test_get_users(client):
    print("Iniciando o teste de obtenção de usuários.")
    rv = client.get('/users')
    print(f"Resposta do GET /users: Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 200
    assert isinstance(rv.data, bytes)
    assert b'"email"' in rv.data

@pytest.mark.timeout(10)
def test_add_user(client):
    print("Iniciando o teste de adição de usuário.")
    data = {
        'name': 'Carlos',
        'email': 'carlos@example.com',
        'age': '25',
        'address': 'Rua C',
        'phone': '999999999',
        'services': 'A,B',
        'expiration_date': '2024-01-01'
    }
    print(f"Enviando dados do usuário: {data}")
    rv = client.post('/add_user', data=data)
    print(f"Resposta do POST /add_user: Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 200
    assert 'Usuário adicionado com sucesso'.encode('utf-8') in rv.data

@pytest.mark.timeout(10)
def test_process_users(client):
    print("Iniciando o teste de processamento de usuários.")
    rv = client.get('/process')
    print(f"Resposta do GET /process: Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 200
    assert 'Processamento concluído'.encode('utf-8') in rv.data

@pytest.mark.timeout(10)
def test_gerar_notas(client):
    print("Iniciando o teste de geração de notas.")
    rv = client.get('/gerar_notas')
    print(f"Resposta do GET /gerar_notas: Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 200
    assert 'Notas geradas e enviadas com sucesso'.encode('utf-8') in rv.data

@pytest.mark.timeout(10)
def test_sql_injection(client):
    print("Iniciando o teste de SQL Injection.")
    data = {
        'name': "' OR '1'='1",
        'email': 'injection@test.com',
        'age': '25',
        'address': 'Rua H',
        'phone': '999999999',
        'services': 'A,B',
        'expiration_date': '2024-01-01'
    }
    print(f"Enviando dados potencialmente maliciosos: {data}")
    rv = client.post('/add_user', data=data)
    print(f"Resposta do POST /add_user (SQL Injection): Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 200
    assert 'Usuário adicionado com sucesso'.encode('utf-8') in rv.data

    rv = client.get('/users')
    print(f"Verificando se a string de injeção de SQL está na resposta: {rv.data}")
    assert b"' OR '1'='1" not in rv.data

@pytest.mark.timeout(10)
def test_missing_required_fields(client):
    print("Iniciando o teste de campos obrigatórios ausentes.")
    data = {
        'name': '',
        'email': 'missing@test.com',
        'age': '25',
        'address': 'Rua I',
        'phone': '999999999',
        'services': 'A,B',
        'expiration_date': '2024-01-01'
    }
    print(f"Enviando dados com campo obrigatório faltando: {data}")
    rv = client.post('/add_user', data=data)
    print(f"Resposta do POST /add_user (campos faltando): Status {rv.status_code}, Dados: {rv.data}")
    assert rv.status_code == 400

@pytest.mark.timeout(10)
def test_performance_get_users(client):
    print("Iniciando o teste de performance para GET /users.")
    start_time = time.time()
    rv = client.get('/users')
    response_time = time.time() - start_time
    print(f"Tempo de resposta do GET /users: {response_time} segundos")
    assert rv.status_code == 200
    assert response_time < 1

@pytest.mark.timeout(10)
def test_performance_add_user(client):
    print("Iniciando o teste de performance para POST /add_user.")
    data = {
        'name': 'PerformanceTest',
        'email': 'performance@test.com',
        'age': '30',
        'address': 'Rua Performance',
        'phone': '999999999',
        'services': 'A,B',
        'expiration_date': '2024-01-01'
    }
    print(f"Enviando dados do usuário para teste de performance: {data}")
    start_time = time.time()
    rv = client.post('/add_user', data=data)
    response_time = time.time() - start_time
    print(f"Tempo de resposta do POST /add_user: {response_time} segundos")
    assert rv.status_code == 200
    assert response_time < 1

@pytest.mark.timeout(10)
def test_load_add_user(client):
    print("Iniciando o teste de carga para adição de múltiplos usuários.")
    for i in range(100):
        data = {
            'name': f'TestUser{i}',
            'email': f'test{i}@example.com',
            'age': '30',
            'address': f'Rua Teste {i}',
            'phone': '999999999',
            'services': 'A,B',
            'expiration_date': '2024-01-01'
        }
        print(f"Adicionando TestUser{i}: {data}")
        rv = client.post('/add_user', data=data)
        print(f"Resposta do POST /add_user para TestUser{i}: Status {rv.status_code}, Dados: {rv.data}")
        assert rv.status_code == 200
        assert 'Usuário adicionado com sucesso'.encode('utf-8') in rv.data
