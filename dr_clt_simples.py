#!/usr/bin/env python3
"""
Dr. CLT - Versão Simplificada (apenas 1 tool para teste)
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

from parlant.sdk import Server, CompositionMode, tool, ToolContext, ToolResult
from parlant.core.nlp.embedding import EmbeddingCache
from supabase_config import log_consulta_clt

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Ferramenta principal do agente
@tool
async def consultar_clt_oficial(context: ToolContext, artigo: str) -> ToolResult:
    """Consulta o texto oficial da CLT no site do Planalto (fonte oficial)"""
    try:
        # URL oficial da CLT no Planalto
        url = "http://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Procurar pelo artigo específico
                    artigo_texto = f"Art. {artigo}"
                    conteudo_artigo = []
                    artigo_encontrado = False
                    
                    for elemento in soup.find_all(text=True):
                        texto = elemento.strip()
                        if texto.startswith(artigo_texto):
                            artigo_encontrado = True
                            conteudo_artigo.append(texto)
                        elif artigo_encontrado:
                            # Continuar coletando até o próximo artigo
                            if texto.startswith('Art. ') and not texto.startswith(artigo_texto):
                                break
                            conteudo_artigo.append(texto)
                    
                    if conteudo_artigo:
                        resultado = "\n".join(conteudo_artigo)
                        await log_consulta_clt("session_teste", "consulta_clt", f"Artigo {artigo}", resultado, [f"Art. {artigo}"])
                        return ToolResult(f"📚 **CLT - Artigo {artigo}**\n\n{resultado}\n\n🌐 Fonte: Planalto Federal")
                    
                    resultado_alternativo = await consultar_clt_senado_alternativo(artigo)
                    return ToolResult(resultado_alternativo)
                
                return ToolResult("❌ Erro ao acessar a CLT do Planalto. Tentando fonte alternativa...")
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta: {str(e)}")

async def consultar_clt_senado_alternativo(artigo: str) -> str:
    """Consulta alternativa no portal do Senado Federal"""
    try:
        url = "http://legis.senado.leg.br/legislacao/ListaPublicacoes.action"
        params = {
            "tipoDocumento": "DL",
            "numero": "5452", 
            "ano": "1943"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    return f"📚 **CLT - Artigo {artigo}**\n\nConsulta via portal do Senado Federal\n\n🌐 Fonte: Senado Federal"
                
                return "❌ Não foi possível acessar as fontes oficiais da CLT."
                
    except Exception as e:
        return f"❌ Erro na consulta alternativa: {str(e)}"

async def main():
    """Função principal para criar e configurar o agente Dr. CLT Simples"""
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    async with Server(port=8803, tool_service_port=8821) as server:
        # Criar o agente Dr. CLT Simples
        agent = await server.create_agent(
            name="Dr. CLT Simples - Teste",
            description="Versão simplificada do advogado trabalhista para teste de embeddings - apenas consulta CLT oficial",
            composition_mode=CompositionMode.FLUID
        )
        
        # Anexar apenas a tool principal
        await agent.attach_tool(
            consultar_clt_oficial,
            "Quando o usuário perguntar sobre artigos da CLT ou legislação trabalhista"
        )
        
        print("🏛️ Dr. CLT Simples - Advogado Trabalhista Virtual iniciado!")
        print("📚 Baseado na CLT oficial e fontes governamentais")
        print("🌐 Acesse: http://localhost:8803")
        print("⚖️ Ferramenta disponível:")
        print("  • Consultar CLT oficial")
        print("\n✅ Servidor rodando! Pressione Ctrl+C para parar")
        
        # Manter o servidor rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dr. CLT Simples finalizado pelo usuário")

if __name__ == "__main__":
    asyncio.run(main())
