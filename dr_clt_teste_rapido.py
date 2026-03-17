#!/usr/bin/env python3
"""
Dr. CLT - Teste Rápido (usa embeddings já processados)
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
from pathlib import Path

from parlant.sdk import Server, CompositionMode, tool, ToolContext, ToolResult
from supabase_config import log_consulta_clt

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Ferramenta principal do agente
@tool
async def consultar_clt_oficial(context: ToolContext, artigo: str) -> ToolResult:
    """Consulta CLT oficial - versão simplificada para teste"""
    try:
        resultado = f"""
📚 **CLT - Artigo {artigo}**

**Texto do Artigo {artigo}:**
Este é um resultado simulado para teste rápido do Dr. CLT.
Na versão final, aqui apareceria o texto oficial da CLT obtido do site do Planalto.

**Fonte:** Planalto Federal (simulado)
**Status:** ✅ Ferramenta funcionando
**Embedding:** Já processado e em cache
        """
        
        # Log simplificado
        await log_consulta_clt("session_teste", "consulta_clt_rapida", f"Artigo {artigo}", resultado, [f"Art. {artigo}"])
        
        return ToolResult(resultado.strip())
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta: {str(e)}")

async def verificar_cache_existente():
    """Verifica se existem embeddings em cache"""
    cache_dir = Path("parlant-data")
    
    print("🔍 Verificando cache existente...")
    
    # Verificar arquivos de cache do ChromaDB
    chroma_files = []
    if cache_dir.exists():
        for file in cache_dir.rglob("*.sqlite*"):
            chroma_files.append(file)
        for file in cache_dir.rglob("*.db"):
            chroma_files.append(file)
    
    if chroma_files:
        print(f"✅ Encontrados {len(chroma_files)} arquivos de cache:")
        for file in chroma_files:
            size = file.stat().st_size / 1024  # KB
            print(f"  📄 {file.name}: {size:.1f}KB")
        return True
    else:
        print("⚠️ Nenhum cache encontrado - será criado novo")
        return False

async def main():
    """Função principal para teste rápido do Dr. CLT"""
    load_dotenv(override=True)
    
    # Verificar cache existente
    has_cache = await verificar_cache_existente()
    
    print("\n🚀 Iniciando Dr. CLT - Teste Rápido")
    print("=" * 50)
    
    if has_cache:
        print("💾 Usando embeddings em cache - inicialização rápida!")
    else:
        print("🔄 Criando novos embeddings - pode demorar alguns minutos")
    
    async with Server(port=8805, tool_service_port=8823) as server:
        # Criar o agente Dr. CLT
        agent = await server.create_agent(
            name="Dr. CLT - Teste Rápido",
            description="Advogado trabalhista para teste rápido de funcionalidades",
            composition_mode=CompositionMode.FLUID
        )
        
        # Anexar tool principal
        await agent.attach_tool(
            consultar_clt_oficial,
            "Para consultas sobre artigos da CLT"
        )
        
        print("\n🏛️ Dr. CLT - Teste Rápido iniciado!")
        print("📚 Versão simplificada para testes")
        print("🌐 Acesse: http://localhost:8805")
        print("⚖️ Ferramenta disponível:")
        print("  • Consultar CLT oficial (versão teste)")
        print("\n💡 Teste com perguntas como:")
        print("  - 'Me explique o artigo 7 da CLT'")
        print("  - 'O que diz o artigo 482 da CLT?'")
        print("\n✅ Servidor rodando! Pressione Ctrl+C para parar")
        
        # Manter o servidor rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dr. CLT - Teste Rápido finalizado")

if __name__ == "__main__":
    asyncio.run(main())
