from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inicial')
def inicial():
    return render_template('inicial.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/resultado', methods=['POST'])
def resultado():

    consumo = int(request.form['consumo'])
    area = int(request.form['area'])
    sombra = request.form['sombra']

    pontos = 0

    # Consumo
    if consumo < 200:
        pontos += 1
    elif consumo <= 500:
        pontos += 2
    else:
        pontos += 3

    # Área
    if area < 20:
        pontos += 1
    elif area <= 50:
        pontos += 2
    else:
        pontos += 3

    # Sombreamento
    if sombra.lower() == "muito":
        pontos += 0
    elif sombra.lower() == "pouco":
        pontos += 2
    else:
        pontos += 3

    # Resultado
       # Resultado
    if pontos <= 3:
        resultado = "Não recomendado"
    elif pontos <= 6:
        resultado = "Parcialmente viável"
    else:
        resultado = "Viável"

    economia = round(consumo * 0.85, 2)

    irradiacao_itamaraca = 5.6

    return render_template(
        'resultado.html',
        resultado=resultado,
        pontos=pontos,
        economia=economia,
        irradiacao=irradiacao_itamaraca
    )



if __name__ == '__main__':
    app.run(debug=True)