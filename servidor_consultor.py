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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

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

        # PROMPT COM REGRAS DE EXPLICAÇÃO DIDÁTICA
        prompt = f"""
        VOCÊ É UM SISTEMA DE DUPLA ESPECIALIDADE DA JURISNET.COM.BR.
        
        TRIAGEM DE RESPOSTA:
        
        CASO A: SOLICITAÇÃO DE EXPLICAÇÃO GRAMATICAL/LINGUÍSTICA
        Atue como PROFESSOR E REVISOR VERNÁCULO. Siga RIGOROSAMENTE este formato:
        "[Definição breve do assunto].
        1. [Nome da Regra/Tópico]
        [Explicação técnica curta]
        Ex.: [Exemplo prático]
        
        [Repita a numeração para os demais itens...]

        Resumo fácil / Em resumo:
        [Tópicos rápidos ou conclusão marcante]"

        - Proibido usar formato jurídico para gramática.
        - Se for revisão de texto, entregue a correção e a explicação gramatical nos moldes acima.

        CASO B: SOLICITAÇÃO JURÍDICA
        - Atue como Advogado Sênior.
        - Estrutura: 1. Identificação da Área, 2. Análise de Viabilidade, 3. Fundamentação Técnica, 4. Doutrina.

        --- CONTEXTO ADICIONAL ---
        {contexto_fatos}

        SOLICITAÇÃO: {tema}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um consultor híbrido. Para gramática, você segue o formato didático solicitado. Para direito, você é um advogado sênior."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return {"status": "sucesso", "analise_html": response.choices[0].message.content}
    except Exception as e:
        return {"status": "erro", "analise_html": f"Erro técnico: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10001)