from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://siata:siata@localhost/siata?options=-c%20search_path=siatasiata'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)


class Restaurante(db.Model):
    identificacionUsuario = db.Column(db.Integer, primary_key=True)
    nombreRestaurante = db.Column(db.String(200), nullable=False)
    valorMenu = db.Column(db.Integer, nullable=False)
    menu = db.Column(db.String(200), nullable=False)
    fechaPago = db.Column(db.DateTime, nullable=False)
    valorPagado = db.Column(db.String(200), nullable=False)
    

    
    def __init__(self,  nombreRestaurante, valorMenu, fechaPago, valorPagado, Menu):
        self.nombreRestaurante = nombreRestaurante
        self.valorMenu = valorMenu
        self.menu = Menu
        self.fechaPago = fechaPago
        self.valorPagado = valorPagado
       
    
       
        
@app.route("/api/pagos", methods=["GET"])
def obtenerTodos():
    restaurantes = Restaurante.query.all()
    return jsonify({"message": "Resultados Extraidos con exito", "restaurantes": str(restaurantes)
                    })
    
@app.route("/api/pagos/<int:restaurante_id>", methods=["PATCH"])
def actualizar(restaurante_id):
    restaurante = Restaurante.query.get(restaurante_id)
    restaurante_valorPagado = request.json['valorPagado']

    
    if restaurante is None:
        abort(404)
        
    else:
        try:
            restaurante_valorPagado = float(restaurante_valorPagado)
        except ValueError:
            return jsonify({"respuesta": "Debe ser un numero"}), 200
        
        restaurante_valorPagado_anterior = float(restaurante.valorPagado)
        restaurante_valorMenu = float(restaurante.valorMenu)
        print(type(restaurante_valorMenu), type(restaurante_valorPagado_anterior))
        valorFaltante = restaurante_valorMenu - restaurante_valorPagado_anterior
        
        if restaurante_valorPagado == valorFaltante :
            restaurante.valorPagado=restaurante_valorPagado_anterior + restaurante_valorPagado
            db.session.add(restaurante)
            db.session.commit()
            return jsonify({"respuesta": "Terminaste de pagar tu abono!"}), 400
        else:
            restaurante.valorPagado=restaurante_valorPagado_anterior + restaurante_valorPagado
            db.session.add(restaurante)
            db.session.commit()
            return jsonify({"respuesta": "Aun quedas debiendo parte de tu abono"}), 400


    
    
    
@app.route("/api/pagos", methods=["POST"])
def registroPagos():
    restaurante_data = request.json
    
    restaurante_nombreRestaurante = restaurante_data['nombreRestaurante']
    if not isinstance(restaurante_nombreRestaurante,str):
        return jsonify({"respuesta": "Formato de nombre incorrecto"}), 400
        
    restaurante_menu = restaurante_data['menu']
    if not isinstance(restaurante_menu,str):
        return jsonify({"respuesta": "Formato de menu incorrecto"}), 400
    
    restaurante_valorMenu = (restaurante_data['valorMenu'])
    try:
        restaurante_valorMenu = float(restaurante_data['valorMenu'])
    except ValueError:
        return jsonify({"respuesta": "Debe ser un numero"}), 200
    restaurante_valorPagado = restaurante_data['valorPagado']
    try:
        restaurante_valorPagado = float(restaurante_data['valorPagado'])
    except ValueError:
        return jsonify({"respuesta": "Debe ser un numero"}), 200
    
    if restaurante_valorPagado < 1 or restaurante_valorPagado > 1000000 :
        return jsonify({"respuesta": "el valor pagado de estar entre 1 y un 1'000.000"}), 400
    
    dia,mes,ano= restaurante_data['fechaPago'].split("/")
    restaurante_fechaPago = ano+'-'+mes+'-'+dia
    today = datetime.now()
    fechaformato = '%Y-%m-%d'
    
    try:
        dateobject = datetime.strptime(restaurante_fechaPago, fechaformato)
        print(dateobject)
        
    except ValueError:
        print("formato de fecha incorrecto, debe ser en formato Año/Mes/Dia")

    restaurante_fechaPago = ano+'-'+mes+'-'+dia
    today = datetime.now()
    fechaformato = '%Y-%m-%d'
    
    try:
        dateobject = datetime.strptime(restaurante_fechaPago, fechaformato)
        print(dateobject)
        if dateobject > today:
            return jsonify({"respuesta": "la fecha debe ser valida"}), 400
        
        if int(dia) %2 == 0 :
            return jsonify({"respuesta": "lo siento pero no se puede recibir el pago por decreto de administración"}), 400
    except ValueError:
        return jsonify({"respuesta": "la fecha debe ser valida"}), 400

        
    
    
    restaurante = Restaurante(nombreRestaurante = restaurante_nombreRestaurante, Menu = restaurante_menu, valorMenu= restaurante_valorMenu, valorPagado= restaurante_valorPagado, fechaPago = restaurante_fechaPago)
    
    db.session.add(restaurante)
    db.session.commit()
    
    if restaurante_valorPagado < restaurante_valorMenu : 
        return jsonify({"respuesta": "gracias por tu abono, sin embargo recuerda que te hace falta pagar $" + str(restaurante_valorMenu-restaurante_valorPagado)}), 200
    else:
        return jsonify({"respuesta": "gracias por pagar todo tu saldo"}), 200
    
 
    
if __name__ == '__main__':
    
    #db.create_all()
    app.run(port=6969)