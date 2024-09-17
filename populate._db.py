import sqlite3
from faker import Faker
import random

# Inicializando Faker para gerar dados fictícios
fake = Faker()

# Conectando ao banco de dados SQLite
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Função para popular o banco de dados
def populate_db(num_records):
    for _ in range(num_records):
        name = fake.name()
        email = fake.email()
        age = random.randint(18, 80)
        address = fake.address().replace('\n', ', ')
        phone = fake.phone_number()
        services = ','.join(random.sample(['A', 'B', 'C', 'D', 'E'], random.randint(1, 3)))
        expiration_date = fake.date_between(start_date='-2y', end_date='+1y')
        notes = ''
        # Inserindo os dados no banco de dados
        c.execute("INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (name, email, age, address, phone, services, expiration_date, notes))
    
    # Salvando as mudanças no banco de dados
    conn.commit()

# Populando o banco de dados com 1000 registros
populate_db(1000)

# Fechando a conexão com o banco de dados
conn.close()

print("Banco de dados populado com sucesso!")
