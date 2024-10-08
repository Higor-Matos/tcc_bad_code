from flask import Flask, request, g
import sqlite3
import smtplib
import datetime
import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

DATABASE = 'database.db'
LOG_FILE = 'process_times.txt'

def log_time(message):
    """Função para salvar o tempo de execução em um arquivo de log."""
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def process_string(s):
    result = ''
    for char in s:
        if char.isupper():
            result += char.lower()
        else:
            result += char.upper()
    return result

# Função de envio de email utilizando o Outlook
def send_email(to_address, subject, body, attachment=None):
    start_time = time.time()
    print(f"MOCK: Simulando envio de e-mail para {to_address}")
    print(f"Assunto: {subject}")
    print(f"Corpo: {body}")
    if attachment:
        print(f"MOCK: Simulando anexo de arquivo {attachment}")
    end_time = time.time()
    time_taken = end_time - start_time
    log_time(f"Tempo para enviar o e-mail: {time_taken:.4f} segundos")

def calculate_price(services, age):
    start_time = time.time()
    total_price = 0
    discount = 0
    tax = 0
    for service in services:
        if service == 'A':
            total_price += 100
        elif service == 'B':
            total_price += 200
        elif service == 'C':
            total_price += 300
        elif service == 'D':
            total_price += 400
        elif service == 'E':
            total_price += 500
        else:
            total_price += 50
    if age > 60:
        discount = total_price * 0.1
    if 'Premium' in services:
        discount += total_price * 0.05
    tax = (total_price - discount) * 0.2
    final_price = total_price - discount + tax
    end_time = time.time()
    time_taken = end_time - start_time
    log_time(f"Tempo para calcular o preço: {time_taken:.4f} segundos")
    return total_price, discount, tax, final_price

def generate_pdf(user_data, prices):
    start_time = time.time()

    # Gerando o HTML
    html = '<html><head><title>Nota de Débito</title></head><body>'
    html += '<h1>Nota de Débito</h1>'
    html += '<p>Nome: ' + process_string(user_data['name']) + '</p>'
    html += '<p>Email: ' + process_string(user_data['email']) + '</p>'
    html += '<p>Endereço: ' + process_string(user_data['address']) + '</p>'
    html += '<p>Telefone: ' + process_string(user_data['phone']) + '</p>'
    html += '<p>Serviços: ' + ', '.join(user_data['services']) + '</p>'
    html += '<p>Preço Total: R$' + str(prices['total_price']) + '</p>'
    html += '<p>Desconto: R$' + str(prices['discount']) + '</p>'
    html += '<p>Imposto: R$' + str(prices['tax']) + '</p>'
    html += '<p>Preço Final: R$' + str(prices['final_price']) + '</p>'
    html += '<p>Data de Vencimento: ' + user_data['expiration_date'] + '</p>'
    html += '<p>Status: ' + user_data['status'] + '</p>'
    html += '</body></html>'
    
    html_file = 'nota_debito_' + str(user_data['id']) + '.html'
    with open(html_file, 'w') as f:
        f.write(html)

    # Gerando o PDF
    pdf_start_time = time.time()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"file:///{html_file}")
    time.sleep(5)
    driver.quit()

    pdf_file = 'nota_debito_' + str(user_data['id']) + '.pdf'
    pdfkit.from_file(html_file, pdf_file)
    pdf_end_time = time.time()

    total_time = time.time() - start_time
    log_time(f"Tempo para gerar HTML e PDF: {total_time:.4f} segundos")
    log_time(f"Tempo específico para gerar PDF: {pdf_end_time - pdf_start_time:.4f} segundos")

    return pdf_file

def process_users():
    start_time = time.time()
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    
    for i in data:
        user_email = i[2]
        user_name = i[1]
        user_age = i[3]
        user_address = i[4]
        user_phone = i[5]
        user_services = i[6].split(',')
        
        # Calcular preço
        total_price, discount, tax, final_price = calculate_price(user_services, user_age)
        
        expiration_date = datetime.datetime.strptime(i[7], '%Y-%m-%d')
        today = datetime.datetime.now()
        days_left = (expiration_date - today).days
        status = ''
        
        if days_left < 0:
            status = 'Expirado'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Expired', i[0]))
            db.commit()
            user_data = {
                'id': i[0],
                'name': user_name,
                'email': user_email,
                'address': user_address,
                'phone': user_phone,
                'services': user_services,
                'expiration_date': i[7],
                'status': status
            }
            prices = {
                'total_price': total_price,
                'discount': discount,
                'tax': tax,
                'final_price': final_price
            }
            
            # Gerar PDF e enviar email
            pdf_file = generate_pdf(user_data, prices)
            email_body = 'Segue em anexo sua nota de débito.'
            send_email(user_email, 'Sua Nota de Débito', email_body, pdf_file)
        elif days_left < 5:
            status = 'Expirando em breve'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Expiring soon', i[0]))
            db.commit()
            reminder = 'Olá ' + user_name + ', sua assinatura irá expirar em ' + str(days_left) + ' dias.'
            send_email(user_email, 'Lembrete de Expiração', reminder)
        else:
            status = 'Ativo'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Active', i[0]))
            db.commit()

    end_time = time.time()
    log_time(f"Tempo total para processar todos os usuários: {end_time - start_time:.4f} segundos")

@app.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    users_list = []
    for i in data:
        user = {
            'id': i[0],
            'name': i[1],
            'email': i[2],
            'age': i[3],
            'address': i[4],
            'phone': i[5],
            'services': i[6],
            'expiration_date': i[7],
            'notes': i[8]
        }
        users_list.append(user)
    return str(users_list)

@app.route('/add_user', methods=['POST'])
def add_user():
    db = get_db()
    c = db.cursor()
    name = request.form['name']
    email = request.form['email']
    age = request.form['age']
    address = request.form['address']
    phone = request.form['phone']
    services = request.form['services']
    expiration_date = request.form['expiration_date']
    notes = ''
    c.execute(f"INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES ('{name}', '{email}', {age}, '{address}', '{phone}', '{services}', '{expiration_date}', '{notes}')")
    db.commit()
    return 'Usuário adicionado com sucesso'

@app.route('/process', methods=['GET', 'POST'])
def process_route():
    process_users()
    return 'Processamento concluído'

app.run(port=5000, use_reloader=False)
