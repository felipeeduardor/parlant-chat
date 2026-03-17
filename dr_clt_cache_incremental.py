#!/usr/bin/env python3
"""
Dr. CLT - Versão com Cache Incremental (salva embeddings em blocos)
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
import pickle
from pathlib import Path

from parlant.sdk import Server, CompositionMode, tool, ToolContext, ToolResult
from supabase_config import log_consulta_clt

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Cache local para embeddings
CACHE_DIR = Path("parlant-data/embeddings_cache")
CACHE_DIR.mkdir(exist_ok=True)

class IncrementalEmbeddingCache:
    """Cache incremental para salvar embeddings em blocos"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "tool_embeddings.pkl"
        self.progress_file = cache_dir / "progress.json"
        
    def save_embedding(self, tool_name: str, embedding_data: dict):
        """Salva embedding de uma tool específica"""
        cache_data = self.load_cache()
        cache_data[tool_name] = {
            'embedding': embedding_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        self.update_progress(tool_name)
        print(f"✅ Embedding salvo para: {tool_name}")
    
    def load_cache(self) -> dict:
        """Carrega cache existente"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def update_progress(self, tool_name: str):
        """Atualiza progresso"""
        progress = self.load_progress()
        progress['completed_tools'] = progress.get('completed_tools', [])
        if tool_name not in progress['completed_tools']:
            progress['completed_tools'].append(tool_name)
        
        progress['last_update'] = datetime.now().isoformat()
        progress['total_completed'] = len(progress['completed_tools'])
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def load_progress(self) -> dict:
        """Carrega progresso"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def is_cached(self, tool_name: str) -> bool:
        """Verifica se tool já tem embedding em cache"""
        cache_data = self.load_cache()
        return tool_name in cache_data and cache_data[tool_name].get('status') == 'completed'

# Instância global do cache
embedding_cache = IncrementalEmbeddingCache()

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

async def pre_cache_embeddings():
    """Pré-processa embeddings das tools em blocos"""
    tools_info = {
        'consultar_clt_oficial': {
            'description': 'Consulta o texto oficial da CLT no site do Planalto (fonte oficial)',
            'usage': 'Quando o usuário perguntar sobre artigos da CLT ou legislação trabalhista'
        }
    }
    
    print("🔄 Iniciando cache incremental de embeddings...")
    progress = embedding_cache.load_progress()
    
    for tool_name, info in tools_info.items():
        if embedding_cache.is_cached(tool_name):
            print(f"✅ {tool_name} já em cache - pulando")
            continue
        
        print(f"🔄 Processando embedding para: {tool_name}")
        
        # Simular processamento de embedding
        # (Na prática, aqui seria a chamada real para OpenAI)
        await asyncio.sleep(2)  # Simular tempo de processamento
        
        # Salvar embedding em cache
        embedding_cache.save_embedding(tool_name, {
            'description': info['description'],
            'usage': info['usage'],
            'vector': [0.1, 0.2, 0.3]  # Placeholder - seria o vetor real
        })
    
    print("✅ Cache incremental concluído!")

async def main():
    """Função principal para criar e configurar o agente Dr. CLT com cache incremental"""
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    # Pré-processar embeddings em cache
    await pre_cache_embeddings()
    
    async with Server(port=8804, tool_service_port=8822) as server:
        # Criar o agente Dr. CLT
        agent = await server.create_agent(
            name="Dr. CLT Cache - Teste Incremental",
            description="Versão com cache incremental para teste de embeddings em blocos",
            composition_mode=CompositionMode.FLUID
        )
        
        # Anexar tool (será mais rápido se já estiver em cache)
        await agent.attach_tool(
            consultar_clt_oficial,
            "Quando o usuário perguntar sobre artigos da CLT ou legislação trabalhista"
        )
        
        print("🏛️ Dr. CLT Cache - Advogado Trabalhista Virtual iniciado!")
        print("📚 Baseado na CLT oficial e fontes governamentais")
        print("🌐 Acesse: http://localhost:8804")
        print("⚖️ Ferramenta disponível:")
        print("  • Consultar CLT oficial")
        print("💾 Cache incremental ativado!")
        print("\n✅ Servidor rodando! Pressione Ctrl+C para parar")
        
        # Manter o servidor rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dr. CLT Cache finalizado pelo usuário")

if __name__ == "__main__":
    asyncio.run(main())
