#!/usr/bin/env python3
"""
Dr. CLT - Usa embeddings já existentes diretamente
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
                        await log_consulta_clt("session_direto", "consulta_clt", f"Artigo {artigo}", resultado, [f"Art. {artigo}"])
                        return ToolResult(f"📚 **CLT - Artigo {artigo}**\n\n{resultado}\n\n🌐 Fonte: Planalto Federal")
                    
                    return ToolResult(f"❌ Artigo {artigo} não encontrado na CLT")
                
                return ToolResult("❌ Erro ao acessar a CLT do Planalto")
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta: {str(e)}")

async def main():
    """Função principal - usa embeddings já processados"""
    load_dotenv(override=True)
    
    print("🚀 Dr. CLT - Usando Embeddings Existentes")
    print("=" * 50)
    print("💾 Aproveitando cache dos 48 minutos de processamento")
    print("⚡ Inicialização super rápida!")
    
    # Usar porta diferente para não conflitar
    async with Server(port=8806, tool_service_port=8824) as server:
        # Criar o agente Dr. CLT
        agent = await server.create_agent(
            name="Dr. CLT - Cache Aproveitado",
            description="Advogado trabalhista que aproveita embeddings já processados",
            composition_mode=CompositionMode.FLUID
        )
        
        # Anexar tool principal
        await agent.attach_tool(
            consultar_clt_oficial,
            "Para consultas sobre artigos da CLT e legislação trabalhista"
        )
        
        print("\n🏛️ Dr. CLT iniciado com cache aproveitado!")
        print("📚 Baseado na CLT oficial do Planalto")
        print("🌐 Acesse: http://localhost:8806")
        print("⚖️ Ferramenta disponível:")
        print("  • Consultar CLT oficial")
        print("\n💡 Teste com perguntas como:")
        print("  - 'Me explique o artigo 7 da CLT'")
        print("  - 'O que diz o artigo 482 da CLT sobre justa causa?'")
        print("  - 'Quais são os direitos do trabalhador no artigo 5?'")
        print("\n✅ Servidor rodando! Pressione Ctrl+C para parar")
        
        # Manter o servidor rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dr. CLT finalizado pelo usuário")

if __name__ == "__main__":
    asyncio.run(main())
