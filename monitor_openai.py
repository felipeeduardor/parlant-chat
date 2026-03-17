#!/usr/bin/env python3
"""
Monitor OpenAI API usage and Parlant process
"""
import psutil
import time
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_openai_usage():
    """Monitora uso da API OpenAI"""
    # Remover conflito se existir
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    load_dotenv(override=True)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "❌ OPENAI_API_KEY não encontrada no .env"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Endpoint para verificar uso (não oficial, mas funciona)
        response = requests.get(
            'https://api.openai.com/v1/models', 
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return f"✅ API OpenAI conectada - {len(response.json()['data'])} modelos disponíveis"
        else:
            return f"⚠️ API OpenAI status: {response.status_code}"
            
    except Exception as e:
        return f"❌ Erro API OpenAI: {str(e)}"

def find_parlant_process():
    """Encontra processo do Parlant"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            if proc.info['cmdline'] and any(script in cmd for cmd in proc.info['cmdline'] 
                                          for script in ['advogado_trabalhista.py', 'dr_clt_simples.py']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def monitor_system():
    """Monitor principal"""
    print("🔍 Monitor Dr. CLT - Parlant")
    print("=" * 50)
    
    start_time = time.time()
    
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        elapsed = int(time.time() - start_time)
        
        print(f"\n⏰ {current_time} | Tempo decorrido: {elapsed//60}m {elapsed%60}s")
        
        # Verificar processo Parlant
        proc = find_parlant_process()
        if proc:
            try:
                cpu = proc.cpu_percent()
                memory = proc.memory_info().rss / 1024 / 1024  # MB
                print(f"🤖 Parlant PID {proc.pid}: CPU {cpu:.1f}% | RAM {memory:.1f}MB")
            except:
                print("🤖 Parlant: processo encontrado mas sem acesso aos dados")
        else:
            print("❌ Processo Parlant não encontrado")
        
        # Verificar API OpenAI
        api_status = get_openai_usage()
        print(f"🔑 {api_status}")
        
        # Verificar arquivos de log
        log_file = "parlant-data/parlant.log"
        if os.path.exists(log_file):
            size = os.path.getsize(log_file) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime("%H:%M:%S")
            print(f"📝 Log: {size:.1f}KB | Última modificação: {mtime}")
        
        # Verificar ChromaDB
        chroma_files = []
        if os.path.exists("parlant-data"):
            for file in os.listdir("parlant-data"):
                if file.endswith(('.sqlite', '.sqlite3', '.db')):
                    chroma_files.append(file)
        
        if chroma_files:
            print(f"🗄️ ChromaDB: {len(chroma_files)} arquivos encontrados")
        else:
            print("🗄️ ChromaDB: nenhum arquivo de banco encontrado")
        
        print("-" * 50)
        time.sleep(10)  # Atualiza a cada 10 segundos

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\n👋 Monitor interrompido pelo usuário")
