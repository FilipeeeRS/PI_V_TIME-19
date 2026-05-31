# PI_V_TIME-19 "PrimeStudy"
Projeto Integrador 5 / Puc Campinas - Engenharia de Software 5º semestre

## 📍 O Projeto
O PrimeStudy é uma plataforma web desenvolvida com o objetivo de otimizar o processo de estudo acadêmico, tornando-o mais eficiente e organizado.
A aplicação permite o upload de arquivos em formato PDF, que são processados por meio de Inteligência Artificial, extraindo as informações mais relevantes, além de dividir os estudos por matérias.

A partir do material enviado, a IA pode gerar:

* Resumos 
* Tópicos 
* Perguntas (Quiz Interativo)
* Flashcards
* Mapa Mental
* Check-lists

## 📍 Integrantes (Time 19):
- [Anderson Lucas do Nascimento Gondim](https://github.com/Ander770) RA: 24787293
- [Felipe Nonato Leoneli](https://github.com/lipeleoneli) RA: 24021973
- [Filipe Ribeiro Simões](https://github.com/FilipeeeRS) RA: 24007657
- [Lucas Albrechet L Ruman](https://github.com/RumanLucas2) RA: 20000626
- [Rafael Roveri Pires](https://github.com/RafssRv) RA: 24007131
- [João Victor Moreira Vidal](https://github.com/JaoVidal1) RA: 19291384

Orientadora:
- Professora SÍLVIA CRISTINA DE MATOS SOARES

-----

## 📍 Tecnologias Utilizadas

  - Linguagem: Python
  - Framework Web: Flask
  - Processamento de PDF: pdfplumber
  - IA Generativa: API do Google Gemini (Google GenAI)
  - Banco de dados: Firebase (Firestore & Authentication)
  - Frontend: HTML5, CSS3, JavaScript
    
-----

## 📍 Como Executar

### Pré-requisitos
- Python 3.10 ou superior instalado
- Conta no [Firebase](https://firebase.google.com/) com projeto criado (Firestore + Authentication habilitados)
- Chave de API do [Google Gemini](https://aistudio.google.com/app/apikey)

---

### Passo 1 — Clone o repositório
```bash
git clone https://github.com/FilipeeeRS/PI_V_TIME-19.git
cd PI_V_TIME-19
```

### Passo 2 — Instale as dependências
```bash
pip install -r requirements.txt
```

### Passo 3 — Configure as credenciais do Firebase
Baixe o arquivo `serviceAccountKey.json` do seu projeto Firebase:
> Firebase Console → Configurações do projeto → Contas de serviço → Gerar nova chave privada

Cole o arquivo `serviceAccountKey.json` dentro da pasta `PrimeStudy/`.

### Passo 4 — Configure as variáveis de ambiente
Crie um arquivo `.env` dentro da pasta `PrimeStudy/` com o seguinte conteúdo:
```env
SECRET_KEY=sua_chave_secreta_flask
GEMINI_API_KEY=sua_chave_api_gemini

FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=...
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...
```
> Os valores do Firebase estão em: Firebase Console → Configurações do projeto → Seus aplicativos → SDK de configuração.

### Passo 5 — Entre na pasta da aplicação
```bash
cd PrimeStudy
```

### Passo 6 — Execute a aplicação
```bash
python app.py
```

### Passo 7 — Acesse no navegador
```
http://127.0.0.1:5000
```
