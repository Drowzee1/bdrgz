import os # Нужна для сохранения файлов
from flask import Flask, redirect, url_for , render_template, request, send_from_directory, flash
from werkzeug.utils import secure_filename
from datetime import timedelta, date
from flask_sqlalchemy import SQLAlchemy

# Этот го***код будет... легендарным!

UPLOAD_FOLDER = './images' # Указывается путь к директории для сохранения файлов, точка нужна для обозначения того, что директория относительная
app = Flask(__name__)
app.secret_key = "SASHAVERNISOTKU"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:eternalblue@localhost/game_shop' #Тут указываются данные для входа в базу данных
db = SQLAlchemy(app)

class Clients(db.Model): # Создание таблицы клиентов
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)  

    def __init__(self, name, email, phone): # Конструктор клиента
        self.name = name
        self.email = email
        self.phone = phone

    def __repr__(self):
        return "<Clients(name='%s', email='%s', phone='%s')>" % (self.name, self.email, self.phone)

class Games(db.Model): # Создание и инициализация таблицы игр. Много спиномозгового текста.
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(80), unique=True, nullable=False)
    genre = db.Column(db.String(32), unique=False, nullable=False)
    release_year = db.Column(db.Integer, unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    pic_url = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Numeric, unique=False, nullable=False)

    def __init__(self, game_name, genre, release_year, qantity, pic_url, price):
        self.game_name = game_name
        self.genre = genre
        self.release_year = release_year
        self.quantity = qantity
        self.pic_url = pic_url
        self.price = price

    def __repr__(self):
        return "<Games(game_name='%s', genre='%s', release_year='%s', quantity='%s', pic_url='%s', price='%s')>" % (self.game_name, self.genre, self.release_year, self.quantity, self.pic_url, self.price)

class Order(db.Model): # Таблица заказов,  включает в себя ID клиента. К одной этой таблице идет отдельно связь от каждого заказанного продукта через промежуточную таблицу order_product
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), unique=False, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), unique=False, nullable=False) 
    order_date = db.Column(db.Date, unique=False, nullable=False) 

    def __init__(self, client_id, game_id, order_date):
        self.client_id = client_id
        self.game_id = game_id
        self.order_date = order_date

@app.route('/addgame/', methods = ["POST", "GET"]) # Форма добавления клиента
def addgame(): 
    if request.method == "POST":                          # При отправлении пост запроса происходит передача данных с помощью request, заполняются переменные
        game_name = request.form["game_name"]             # соответствующие элементу класса, потом создается экземпляр класса, являющийся строкой базы данный. 
        genre = request.form["genre"]                     # Далее он вносится в базу данных коммитом. 
        release_year = request.form["release_year"]
        quantity = request.form["quantity"]
        price = request.form.get("price")
        file = request.files['pic']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pic_url = url_for('uploaded_file', filename=filename)
        new_game = Games(game_name, genre, release_year, quantity, pic_url, price)
        db.session.add(new_game)
        db.session.commit()
        return redirect("http://127.0.0.1:5000/games/")      
    else:
        return render_template("addgame.html")

@app.route('/addclient/', methods = ["POST", "GET"])
def addclient(): 
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        new_client = Clients(name, email, phone)
        db.session.add(new_client)
        db.session.commit()
        return redirect("http://127.0.0.1:5000/clients/")
    else:
        return render_template("addclient.html")

@app.route('/addorder/', methods = ["POST", "GET"])
def addorder(): 
    rows = Clients.query.count()
    clientura = []
    for x in range (1, rows+1):                 # Здесь я решил сделать поля самозаполняющимися, для предотвращения ошибок и простоты. Для этого циклом
        pupa = Clients.query.get(x)             # считываются имена клиентов и игр по айдишникам из таблицы заказов, а потом выводятся вместе с ними.
        clientura.append(pupa.name)
    rows1 = Games.query.count()
    gamez = []
    for x in range (1, rows1+1):
        lupa = Games.query.get(x)
        gamez.append(lupa.game_name)

    if request.method == "POST":
        client_id = request.form["name"]
        game_id = request.form["game_name"]
        order_date = date.today()
        new_order = Order(client_id, game_id, order_date)
        db.session.add(new_order)
        db.session.commit()
        return redirect("http://127.0.0.1:5000/orders/")
    else:
        return render_template("addorder.html", rows = rows, rows1=rows1, clientura = clientura, gamez=gamez)

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/clients/', methods = ["POST", "GET"])
def tableclient():
    if request.method == "POST": # После проверки критерия идет поиск первой записи по нему.
        rows = 1
        transfer = []
        if request.form["criteria"] == "name":
            pupa = Clients.query.filter_by(name=request.form["search"]).first()
        elif request.form["criteria"] == "email":
            pupa = Clients.query.filter_by(email=request.form["search"]).first()
        elif request.form["criteria"] == "phone":
            pupa = Clients.query.filter_by(phone=request.form["search"]).first()
        transfer.append(pupa)
        return render_template("tableclient.html", rows = rows, transfer = transfer)  
    else:
        rows = Clients.query.count()
        transfer = []
        for x in range (1, rows+1):
            pupa = Clients.query.get(x)
            transfer.append(pupa)
        return render_template("tableclient.html", rows = rows, transfer = transfer)  

@app.route('/games/', methods = ["POST", "GET"])
def tablegame():
    if request.method == "POST": # после проверки критерия идет подсчет строк, которые нужно будет вывести, а потом выполняется SQL запрос,  
        transfer = []            # результаты которого аппендятся в трансфер массив запросами first по перебираемым ID.
        i = 0

        if request.form["criteria"] == "game_name":
            rows = Games.query.filter_by(game_name=request.form["search"]).count()
            result = db.session.execute("SELECT * FROM games WHERE game_name = :val", {'val': request.form["search"]})

        elif request.form["criteria"] == "genre":
            rows = Games.query.filter_by(genre=request.form["search"]).count()
            result = db.session.execute("SELECT * FROM games WHERE genre = :val", {'val': request.form["search"]})

        elif request.form["criteria"] == "release_year":
            if request.form["search"].isdigit():
                rows = Games.query.filter_by(release_year=request.form["search"]).count()
                result = db.session.execute("SELECT * FROM games WHERE release_year = :val", {'val': request.form["search"]})
            else:
                flash("Год должен состоять из цифр!")
                return redirect("http://127.0.0.1:5000/games/")

        elif request.form["criteria"] == "quantity":
            if request.form["search"].isdigit():
                rows = Games.query.filter_by(quantity=request.form["search"]).count()
                result = db.session.execute("SELECT * FROM games WHERE quantity = :val", {'val': request.form["search"]})
            else:
                flash("Количество должно состоять из цифр!")
                return redirect("http://127.0.0.1:5000/games/")

        elif request.form["criteria"] == "price":
            if request.form["search"].isdigit():
                rows = Games.query.filter_by(price=request.form["search"]).count()
                result = db.session.execute("SELECT * FROM games WHERE price = :val", {'val': request.form["search"]})
            else:
                flash("Цена должна состоять из цифр!")
                return redirect("http://127.0.0.1:5000/games/")

        aids = [row[0] for row in result] # Тут я еще не допер как извлечь возврат
        for aid in aids:
            pupa = Games.query.filter_by(id=aids[i]).first()
            i=i+1
            transfer.append(pupa) 
        return render_template("tablegame.html", rows = rows, transfer = transfer)
    else:
        rows = Games.query.count()
        transfer = []
        for x in range (1, rows+1):
            pupa = Games.query.get(x)
            transfer.append(pupa)
        return render_template("tablegame.html", rows = rows, transfer = transfer) 

@app.route('/orders/', methods = ["POST", "GET"])
def tableorder():
    if request.method == "POST":  # И ТУТ Я НАКОНЕЦ ДОПЕР
        if request.form["criteria"] == "client_id":
            if request.form["search"].isdigit():
                result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where o.client_id= :val", {'val': request.form["search"]})
                transfer = list(result)
                rows=len(transfer)
            else:
                flash("ID клиента должен состоять из цифр!")
                return redirect("http://127.0.0.1:5000/orders/")
        elif request.form["criteria"] == "name":
            result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where c.name= :val", {'val': request.form["search"]})
            transfer = list(result)
            rows=len(transfer)
        elif request.form["criteria"] == "email":
            result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where c.email= :val", {'val': request.form["search"]})
            transfer = list(result)
            rows=len(transfer)
        elif request.form["criteria"] == "game_id":
            if request.form["search"].isdigit():
                result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where o.game_id= :val", {'val': request.form["search"]})
                transfer = list(result)
                rows=len(transfer)
            else:
                flash("ID игры должен состоять из цифр!")
                return redirect("http://127.0.0.1:5000/orders/")
        elif request.form["criteria"] == "game_name":
            result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where g.game_name= :val", {'val': request.form["search"]})
            transfer = list(result)
            rows=len(transfer)
        elif request.form["criteria"] == "order_date":
            result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id where o.order_date= :val", {'val': request.form["search"]})
            transfer = list(result)
            rows=len(transfer)
        return render_template("tableorder.html", transfer = transfer, rows = rows)

    else:
        result = db.session.execute("select o.*, c.name, c.email, g.game_name from clients c inner join public.order o on c.id=o.client_id inner join games g on o.game_id=g.id")
        transfer = list(result)
        rows=len(transfer)
        return render_template("tableorder.html", transfer = transfer, rows = rows)

        # rows = Order.query.count()
        # transfer = []
        # temp_name = []
        # temp_game_name = []
        # for x in range (1, rows+1):
        #     pupa = Order.query.get(x)
        #     transfer.append(pupa)
        #     temp_name.append(Clients.query.get(transfer[x-1].client_id))
        #     temp_game_name.append(Games.query.get(transfer[x-1].game_id))
        # return render_template("tableorder.html", rows = rows, transfer = transfer, name = temp_name, game_name = temp_game_name) 

@app.route('/game')
def game():
    # data = Games.query.get(1)
    rows = Games.query.count()
    return f"{rows}"

if __name__ == '__main__':
    app.run(debug=True)