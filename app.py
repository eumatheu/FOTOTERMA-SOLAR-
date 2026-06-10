from flask import Flask, render_template, request, redirect, url_for, session
import math
from banco import (salvar_atendimento, listar_atendimentos, buscar_atendimento,
                   deletar_atendimento, atualizar_atendimento, cadastrar_usuario, verificar_login)

app = Flask(__name__)
app.secret_key = "fototerma_secret_2026"  # necessário para usar session

# ── Base de dados LABREN / INPE ───────────────────────────────────────────────
PONTOS_LABREN = {
    42560: {
        'nome'  : 'Itapissuma (sul da ilha)',
        'lat'   : -7.7684,
        'lon'   : -34.8974,
        'irrad' : 5.518,
    },
    42951: {
        'nome'  : 'Ilha de Itamaracá (centro/norte)',
        'lat'   : -7.7481,
        'lon'   : -34.8306,
        'irrad' : 5.532,
    },
}

# ── Funções auxiliares ────────────────────────────────────────────────────────

def calcular(consumo, area_disp, tarifa, sombra,
             potencia_painel, largura_painel, altura_painel, irradiacao):
    area_painel  = largura_painel * altura_painel
    perda_padrao = 0.20
    perda_sombra = sombra / 100.0
    perda_total  = perda_padrao + perda_sombra

    if perda_total >= 1.0:
        return None

    eficiencia_final    = 1.0 - perda_total
    potencia_necessaria = (consumo / 30) / (irradiacao * eficiencia_final)
    num_paineis         = math.ceil((potencia_necessaria * 1000) / potencia_painel)
    potencia_real       = (num_paineis * potencia_painel) / 1000
    area_nec            = num_paineis * area_painel
    investimento        = potencia_real * 4000
    eco_anual           = (consumo * tarifa) * 12
    payback             = investimento / eco_anual if eco_anual > 0 else 0
    roi                 = (((eco_anual * 25) - investimento) / investimento) * 100
    lucro_liquido       = (eco_anual * 25) - investimento

    if area_disp < area_nec:
        status = "Inviável por espaço"
    elif sombra > 30:
        status = "Alerta de eficiência"
    else:
        status = "Totalmente viável"

    return {
        'eficiencia'   : round(eficiencia_final * 100, 1),
        'num_paineis'  : num_paineis,
        'area_nec'     : round(area_nec, 1),
        'investimento' : round(investimento, 2),
        'payback'      : round(payback, 1),
        'roi'          : round(roi, 1),
        'lucro_liquido': round(lucro_liquido, 2),
        'status'       : status,
    }
def buscar_irradiacao(ponto_id):
    for id_ponto, dados in PONTOS_LABREN.items():
        if id_ponto == ponto_id:
            return dados['irrad']

    return None

# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/inicial')
def inicial():
    return render_template('inicial.html', pontos_labren=PONTOS_LABREN)

# ── Login ─────────────────────────────────────────────────────────────────────

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email  = request.form.get('email', '').strip()
    senha  = request.form.get('senha', '').strip()
    perfil = request.form.get('perfil', 'consultor')

    usuario = verificar_login(email, senha, perfil)

    if usuario is None:
        return render_template('login.html', erro="E-mail, senha ou perfil incorretos.")

    # Salva dados do usuário na sessão
    session['usuario_id']   = usuario['id']
    session['usuario_nome'] = usuario['nome']
    session['usuario_perfil'] = usuario['perfil']

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── Cadastro ──────────────────────────────────────────────────────────────────

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/cadastro', methods=['POST'])
def cadastrar():
    nome       = request.form.get('nome', '').strip()
    email      = request.form.get('email', '').strip()
    senha      = request.form.get('senha', '').strip()
    senha_conf = request.form.get('senha_conf', '').strip()
    perfil     = request.form.get('perfil', 'consultor')

    if not nome or not email or not senha:
        return render_template('cadastro.html', erro="Preencha todos os campos obrigatórios.")

    if senha != senha_conf:
        return render_template('cadastro.html', erro="As senhas não coincidem.")

    dados = {
        'nome'    : nome,
        'email'   : email,
        'senha'   : senha,
        'perfil'  : perfil,
        'registro': request.form.get('registro', '').strip() or None,
        'endereco': request.form.get('endereco', '').strip() or None,
        'regiao'  : request.form.get('regiao') or None,
    }

    id_novo = cadastrar_usuario(dados)

    if id_novo is None:
        return render_template('cadastro.html', erro="Este e-mail já está cadastrado.")

    return redirect(url_for('login'))

# ── Atendimentos ──────────────────────────────────────────────────────────────

@app.route('/clientes')
def clientes():
    atendimentos = listar_atendimentos()
    return render_template('clientes.html', atendimentos=atendimentos)

@app.route('/atendimento/<int:id>/editar')
def editar_atendimento(id):
    atendimento = buscar_atendimento(id)
    if atendimento is None:
        return "Atendimento não encontrado.", 404
    return render_template('editar.html', a=atendimento)

@app.route('/atendimento/<int:id>/editar', methods=['POST'])
def salvar_edicao(id):
    try:
        nome            = request.form['nome'].strip()
        endereco        = request.form['endereco'].strip()
        consumo         = float(request.form['consumo'])
        area_disp       = float(request.form['area'])
        tarifa          = float(request.form['tarifa'])
        sombra          = float(request.form['sombra'])
        potencia_painel = float(request.form.get('potencia_placa') or 550)
        largura_painel  = float(request.form.get('largura_placa')  or 1.13)
        altura_painel   = float(request.form.get('altura_placa')   or 2.20)
    except (ValueError, KeyError):
        return "Erro: preencha todos os campos corretamente.", 400
    ponto_id = int(request.form.get('regiao') or 42951)

    irradiacao = buscar_irradiacao(ponto_id)

    if irradiacao is None:
        return "Ponto LABREN não encontrado.", 400

    res = calcular(
        consumo,
        area_disp,
        tarifa,
        sombra,
        potencia_painel,
        largura_painel,
        altura_painel,
        irradiacao
    )
    

    res = calcular(consumo, area_disp, tarifa, sombra,
                   potencia_painel, largura_painel, altura_painel, irradiacao)

    if res is None:
        return render_template('resultado.html', modo='inviavel', nome=nome)

    dados = {
        'nome'          : nome,
        'endereco'      : endereco,
        'consumo'       : consumo,
        'tarifa'        : tarifa,
        'area_disp'     : area_disp,
        'sombra'        : sombra,
        'potencia_placa': potencia_painel,
        'largura_placa' : largura_painel,
        'altura_placa'  : altura_painel,
        'ponto_labren'  : ponto_id,
        'irradiacao'    : irradiacao,
        'num_paineis'   : res['num_paineis'],
        'area_nec'      : res['area_nec'],
        'investimento'  : res['investimento'],
        'payback'       : res['payback'],
        'roi'           : res['roi'],
        'lucro_liquido' : res['lucro_liquido'],
        'status'        : res['status'],
    }

    atualizar_atendimento(id, dados)
    return redirect(url_for('ver_atendimento', id=id))

@app.route('/atendimento/<int:id>')
def ver_atendimento(id):
    atendimento = buscar_atendimento(id)
    if atendimento is None:
        return "Atendimento não encontrado.", 404
    return render_template('resultado.html', a=atendimento, modo='detalhe')

@app.route('/atendimento/<int:id>/deletar', methods=['POST'])
def deletar(id):
    deletar_atendimento(id)
    return redirect(url_for('clientes'))

@app.route('/resultado', methods=['POST'])
def resultado():
    try:
        nome            = request.form['nome'].strip()
        endereco        = request.form['endereco'].strip()
        consumo         = float(request.form['consumo'])
        area_disp       = float(request.form['area'])
        tarifa          = float(request.form['tarifa'])
        sombra          = float(request.form['sombra'])
        potencia_painel = float(request.form.get('potencia_placa') or 550)
        largura_painel  = float(request.form.get('largura_placa')  or 1.13)
        altura_painel   = float(request.form.get('altura_placa')   or 2.20)
    except (ValueError, KeyError):
        return "Erro: preencha todos os campos corretamente.", 400
    ponto_id = int(request.form.get('regiao') or 42951)

    irradiacao = buscar_irradiacao(ponto_id)

    if irradiacao is None:
        return "Ponto LABREN não encontrado.", 400

    res = calcular(
        consumo,
        area_disp,
        tarifa,
        sombra,
        potencia_painel,
        largura_painel,
        altura_painel,
        irradiacao
    )
    

    res = calcular(consumo, area_disp, tarifa, sombra,
                   potencia_painel, largura_painel, altura_painel, irradiacao)

    if res is None:
        return render_template('resultado.html', modo='inviavel', nome=nome)

    dados = {
        'nome'          : nome,
        'endereco'      : endereco,
        'consumo'       : consumo,
        'tarifa'        : tarifa,
        'area_disp'     : area_disp,
        'sombra'        : sombra,
        'potencia_placa': potencia_painel,
        'largura_placa' : largura_painel,
        'altura_placa'  : altura_painel,
        'ponto_labren'  : ponto_id,
        'irradiacao'    : irradiacao,
        'num_paineis'   : res['num_paineis'],
        'area_nec'      : res['area_nec'],
        'investimento'  : res['investimento'],
        'payback'       : res['payback'],
        'roi'           : res['roi'],
        'lucro_liquido' : res['lucro_liquido'],
        'status'        : res['status'],
    }

    id_salvo = salvar_atendimento(dados)
    return redirect(url_for('ver_atendimento', id=id_salvo))


if __name__ == '__main__':
    app.run(debug=True)