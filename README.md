Funcionalidades:
Cadastro de usuário com perfis (consultor ou cliente);
Login e autenticação de usuários;
Cadastro de análises de viabilidade;
Consulta de análises já realizadas;
Edição de análises existentes;
Exclusão de análises;
Integração com dados de irradiação solar da API LABREN;

Cálculo automático de:
Quantidade de painéis necessários;
Área necessária para instalação;
Investimento estimado;
Payback;
ROI (Retorno sobre Investimento);
Lucro líquido projetado.

Tecnologias utilizadas:
Python;
SQLite;
API LABREN;
Hash SHA-256 para armazenamento seguro de senhas;

Estrutura:
O sistema utiliza um banco SQLite (fototerma.db) contendo:
Usuários;
Nome;
E-mail;
Senha criptografada;
Perfil (consultor ou cliente);
Registro profissional;
Endereço;
Região;
Atendimentos;
Dados do cliente;
Consumo de energia;
Tarifa elétrica;
Área disponível;
Nível de sombreamento;
Dados dos painéis;
Irradiação solar;
Indicadores financeiros;
Status da análise.

Como executar:
1- Abra um novo folder
2-Abra o terminal integrado do github: dentro do folder, clique com o botão direito em "abrir em terminal integrado" ou "open in integrated terminal"
3- Clone o repositório
git clone -b main https://github.com/eumatheu/FOTOTERMA-SOLAR-
4- Instale o flask
pip instal flask
5- Agora clique com o botão direito em app.py, volte ao terminal integrado e digite python app.py para executar a aplicação em um servidor de desenvolvimento
6- Acesse o link (pode usar control + click no link para abrí-lo)
