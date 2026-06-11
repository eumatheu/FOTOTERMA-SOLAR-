## Funcionalidades

* Cadastro de usuários com perfis (consultor ou cliente)
* Login e autenticação de usuários
* Cadastro de análises de viabilidade
* Consulta de análises já realizadas
* Edição de análises existentes
* Exclusão de análises
* Integração com dados de irradiação solar da API LABREN

### Cálculos automáticos

* Quantidade de painéis necessários
* Área necessária para instalação
* Investimento estimado
* Payback
* ROI (Retorno sobre Investimento)
* Lucro líquido projetado

## Tecnologias utilizadas

* Python
* SQLite
* API LABREN
* Hash SHA-256 para armazenamento seguro de senhas

## Estrutura

O sistema utiliza um banco SQLite (`fototerma.db`) contendo:

### Usuários

* Nome
* E-mail
* Senha criptografada
* Perfil (consultor ou cliente)
* Registro profissional
* Endereço
* Região

### Atendimentos

* Dados do cliente
* Consumo de energia
* Tarifa elétrica
* Área disponível
* Nível de sombreamento
* Dados dos painéis
* Irradiação solar
* Indicadores financeiros
* Status da análise

## Como executar

1. Abra uma pasta vazia no VS Code.

2. Abra o terminal integrado:

   * Clique com o botão direito na pasta e selecione **"Open in Integrated Terminal"** ou **"Abrir em Terminal Integrado"**.

3. Clone o repositório:

```bash
git clone -b main https://github.com/eumatheu/FOTOTERMA-SOLAR-.git
```

4. Entre na pasta do projeto:

```bash
cd FOTOTERMA-SOLAR-
```

5. Instale o Flask:

```bash
pip install flask
```

6. Execute a aplicação:

```bash
python app.py
```

7. Acesse o endereço exibido no terminal (geralmente `http://127.0.0.1:5000`).
