import os
import io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from openai import OpenAI
from typing import List
import uvicorn

# ==============================
# 🔐 CONFIGURAÇÃO DE ALTA FIDELIDADE
# ==============================
# Prioriza a variável de ambiente do Render para segurança máxima
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="JurisNet Engine Sênior")

# Configuração de CORS para permitir comunicação com o seu domínio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

@app.post("/consultoria-analise")
async def endpoint_consultor(
    tema: str = Form(...),
    arquivos: List[UploadFile] = File(None)
):
    try:
        contexto_fatos = ""
        if arquivos:
            for arq in arquivos:
                dados = await arq.read()
                if arq.filename.lower().endswith(".pdf"):
                    pdf = PdfReader(io.BytesIO(dados))
                    contexto_fatos += "".join(p.extract_text() or "" for p in pdf.pages)
                else:
                    contexto_fatos += dados.decode("utf-8", errors="ignore")

        # PROMPT DE ALTA COMPLEXIDADE JURÍDICA E DIDÁTICA
        prompt = f"""
        VOCÊ É UM CONSULTOR JURÍDICO SÊNIOR E ESPECIALISTA EM LÍNGUA PORTUGUESA DA JURISNET.COM.BR.
        
        TRIAGEM DE RESPOSTA (DECIDA O FORMATO PELO CONTEÚDO):
        
        CASO A: SOLICITAÇÃO LINGUÍSTICA (Gramática, Revisão, Dúvidas de Português)
        Siga RIGOROSAMENTE este formato didático:
        "[Definição breve do assunto].
        1. [Nome da Regra/Tópico]
        [Explicação técnica curta]
        Ex.: [Exemplo prático]
        
        [Repita para os demais itens...]

        Resumo fácil / Em resumo:
        [Tópicos rápidos ou conclusão]"

        CASO B: SOLICITAÇÃO JURÍDICA (Consultoria, Análise de Fatos, Leis)
        Atue como Advogado Sênior e Estruture OBRIGATORIAMENTE assim:
        
        1. **Introdução**: Apresentação técnica e resumida do tema jurídico.
        2. **O que diz a Lei**: Citação detalhada de artigos (Código Civil, CPC, CLT, CP, CF) pertinentes ao tema. Simule uma busca na rede para precisão.
        3. **Requisitos**: Listar as condições necessárias para a existência ou exercício do direito em questão.
        4. **Exemplo Prático**: Uma situação hipotética para ilustrar a aplicação da norma.
        5. **Procedimento da Ação Judicial**: Explicar o rito processual, onde protocolar e como funciona o trâmite.
        6. **Tópicos Específicos (Provas)**: Detalhar o rol de documentos e evidências indispensáveis.
        7. **Análise do Caso Concreto**: Aplicação direta de toda a fundamentação acima aos fatos narrados pelo usuário.

        --- CONTEXTO DOS DOCUMENTOS ANEXADOS ---
        {contexto_fatos}

        SOLICITAÇÃO DO USUÁRIO: {tema}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um jurista e filólogo sênior. Suas respostas jurídicas devem ser exaustivas e seguir a estrutura de 7 tópicos. Suas respostas gramaticais devem ser didáticas e numeradas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1 # Mantém a precisão técnica e evita alucinações
        )
        
        # Retorna o conteúdo formatado
        return {"status": "sucesso", "analise_html": response.choices[0].message.content}

    except Exception as e:
        return {"status": "erro", "analise_html": f"Erro técnico no processamento: {str(e)}"}

if __name__ == "__main__":
    # Rodar uvicorn servidor_consultor:app --port 10001
    uvicorn.run(app, host="0.0.0.0", port=10001)