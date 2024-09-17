from flask import Flask, request
import sqlite3
import smtplib
import datetime
import random
import pdfkit

app = Flask(__name__)

conn=sqlite3.connect('database.db')
c=conn.cursor()
# Criando a tabela de usuários diretamente no código, misturando SQL com Python
c.execute('''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    age INTEGER,
    address TEXT,
    phone TEXT,
    services TEXT,
    expiration_date TEXT,
    notes TEXT
    )''')
conn.commit()
# Inserindo dados diretamente na tabela sem verificar se já existem
c.execute("INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES ('João', 'joao@example.com', 65, 'Rua A', '123456789', 'A,B,C', '2021-10-01', '')")
c.execute("INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES ('Maria', 'maria@example.com', 30, 'Rua B', '987654321', 'B,C,D', '2023-12-31', '')")
conn.commit()

# Função ineficiente para processar strings
def process_string(s):
    result = ''
    for char in s:
        if char.isupper():
            result += char.lower()
        else:
            result += char.upper()
    # Simulando uma operação complexa desnecessária
    for i in range(1000):
        result = ''.join([c for c in reversed(result)])
    return result

# Função mal projetada para enviar email sem segurança
def send_email(to_address, subject, body, attachment=None):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    # Credenciais expostas no código
    server.login('seu_email@gmail.com','sua_senha')
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    msg = MIMEMultipart()
    msg['From'] = 'seu_email@gmail.com'
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if attachment:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(attachment, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment}"')
        msg.attach(part)
    server.sendmail('seu_email@gmail.com',to_address,msg.as_string())
    server.close()

# Função ineficiente para calcular preços
def calculate_price(services, age):
    total_price = 0
    discount = 0
    tax = 0
    # Processamento ineficiente dos serviços
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
    return total_price, discount, tax, final_price

# Função mal projetada para gerar PDF
def generate_pdf(user_data, prices):
    # Gerando HTML diretamente no código
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
    # Salvando HTML em um arquivo temporário
    html_file = 'nota_debito_' + str(user_data['id']) + '.html'
    with open(html_file, 'w') as f:
        f.write(html)
    # Convertendo HTML para PDF usando pdfkit (ineficiente)
    pdf_file = 'nota_debito_' + str(user_data['id']) + '.pdf'
    pdfkit.from_file(html_file, pdf_file)
    return pdf_file

# Função mal organizada para processar usuários
def process_users():
    c.execute("SELECT * FROM users")
    data=c.fetchall()
    for i in data:
        user_email = i[2]
        user_name = i[1]
        user_age = i[3]
        user_address = i[4]
        user_phone = i[5]
        user_services = i[6].split(',')
        total_price, discount, tax, final_price = calculate_price(user_services, user_age)
        expiration_date = datetime.datetime.strptime(i[7], '%Y-%m-%d')
        today = datetime.datetime.now()
        days_left = (expiration_date - today).days
        status = ''
        if days_left < 0:
            status = 'Expirado'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Expired', i[0]))
            conn.commit()
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
            pdf_file = generate_pdf(user_data, prices)
            email_body = 'Segue em anexo sua nota de débito.'
            send_email(user_email, 'Sua Nota de Débito', email_body, pdf_file)
        elif days_left < 5:
            status = 'Expirando em breve'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Expiring soon', i[0]))
            conn.commit()
            # Enviar email de lembrete
            reminder = 'Olá ' + user_name + ', sua assinatura irá expirar em ' + str(days_left) + ' dias.'
            send_email(user_email, 'Lembrete de Expiração', reminder)
        else:
            status = 'Ativo'
            c.execute("UPDATE users SET notes=? WHERE id=?", ('Active', i[0]))
            conn.commit()

# Função para retornar dados do banco de dados (endpoint adicional)
@app.route('/users', methods=['GET'])
def get_users():
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
    return str(users_list)  # Retornando dados como string sem formatação adequada

# Endpoint para adicionar usuário sem validação adequada
@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    age = request.form['age']
    address = request.form['address']
    phone = request.form['phone']
    services = request.form['services']
    expiration_date = request.form['expiration_date']
    notes = ''
    # Inserindo dados sem sanitização ou validação
    c.execute(f"INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES ('{name}', '{email}', {age}, '{address}', '{phone}', '{services}', '{expiration_date}', '{notes}')")
    conn.commit()
    return 'Usuário adicionado com sucesso'

# Endpoint para processar usuários
@app.route('/process', methods=['GET', 'POST'])
def process_route():
    process_users()
    return 'Processamento concluído'

# O app Flask está sendo executado na porta 5000 sem mensagens ou logs
app.run(port=5000)
