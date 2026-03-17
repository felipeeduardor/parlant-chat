# supabase_config.py
# Configuração e integração com Supabase para armazenar dados do Dr. CLT

import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class SupabaseManager:
    """Gerenciador de conexão e operações com Supabase"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configuradas nas variáveis de ambiente")
        
        self.supabase: Client = create_client(self.url, self.key)
    
    async def create_tables(self):
        """Cria as tabelas necessárias no Supabase"""
        
        # Tabela para armazenar consultas realizadas
        consultas_table = """
        CREATE TABLE IF NOT EXISTS consultas_clt (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            tipo_consulta VARCHAR(100),
            pergunta TEXT,
            resposta TEXT,
            artigos_consultados TEXT[],
            created_at TIMESTAMP DEFAULT NOW(),
            user_ip VARCHAR(45),
            user_agent TEXT
        );
        """
        
        # Tabela para armazenar cálculos de rescisão
        calculos_table = """
        CREATE TABLE IF NOT EXISTS calculos_rescisao (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            salario DECIMAL(10,2),
            meses_trabalhados INTEGER,
            tipo_demissao VARCHAR(50),
            resultado JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Tabela para feedback dos usuários
        feedback_table = """
        CREATE TABLE IF NOT EXISTS feedback_usuarios (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comentario TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Tabela para estatísticas de uso
        estatisticas_table = """
        CREATE TABLE IF NOT EXISTS estatisticas_uso (
            id SERIAL PRIMARY KEY,
            data DATE DEFAULT CURRENT_DATE,
            total_consultas INTEGER DEFAULT 0,
            total_calculos INTEGER DEFAULT 0,
            artigos_mais_consultados JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(data)
        );
        """
        
        try:
            # Executar criação das tabelas
            self.supabase.postgrest.rpc('exec_sql', {'sql': consultas_table}).execute()
            self.supabase.postgrest.rpc('exec_sql', {'sql': calculos_table}).execute()
            self.supabase.postgrest.rpc('exec_sql', {'sql': feedback_table}).execute()
            self.supabase.postgrest.rpc('exec_sql', {'sql': estatisticas_table}).execute()
            
            print("✅ Tabelas criadas com sucesso no Supabase")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {str(e)}")
    
    def salvar_consulta(self, session_id: str, tipo_consulta: str, pergunta: str, 
                       resposta: str, artigos_consultados: List[str] = None,
                       user_ip: str = None, user_agent: str = None) -> bool:
        """Salva uma consulta realizada pelo usuário"""
        
        try:
            data = {
                'session_id': session_id,
                'tipo_consulta': tipo_consulta,
                'pergunta': pergunta,
                'resposta': resposta,
                'artigos_consultados': artigos_consultados or [],
                'user_ip': user_ip,
                'user_agent': user_agent
            }
            
            result = self.supabase.table('consultas_clt').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar consulta: {str(e)}")
            return False
    
    def salvar_calculo_rescisao(self, session_id: str, salario: float, 
                               meses_trabalhados: int, tipo_demissao: str,
                               resultado: Dict[str, Any]) -> bool:
        """Salva um cálculo de rescisão realizado"""
        
        try:
            data = {
                'session_id': session_id,
                'salario': salario,
                'meses_trabalhados': meses_trabalhados,
                'tipo_demissao': tipo_demissao,
                'resultado': json.dumps(resultado)
            }
            
            result = self.supabase.table('calculos_rescisao').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar cálculo: {str(e)}")
            return False
    
    def salvar_feedback(self, session_id: str, rating: int, comentario: str = None) -> bool:
        """Salva feedback do usuário"""
        
        try:
            data = {
                'session_id': session_id,
                'rating': rating,
                'comentario': comentario
            }
            
            result = self.supabase.table('feedback_usuarios').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar feedback: {str(e)}")
            return False
    
    def obter_estatisticas_hoje(self) -> Dict[str, Any]:
        """Obtém estatísticas de uso do dia atual"""
        
        try:
            hoje = datetime.now().date()
            
            # Consultas do dia
            consultas_hoje = self.supabase.table('consultas_clt')\
                .select('*')\
                .gte('created_at', f'{hoje} 00:00:00')\
                .lt('created_at', f'{hoje} 23:59:59')\
                .execute()
            
            # Cálculos do dia
            calculos_hoje = self.supabase.table('calculos_rescisao')\
                .select('*')\
                .gte('created_at', f'{hoje} 00:00:00')\
                .lt('created_at', f'{hoje} 23:59:59')\
                .execute()
            
            # Feedback do dia
            feedback_hoje = self.supabase.table('feedback_usuarios')\
                .select('rating')\
                .gte('created_at', f'{hoje} 00:00:00')\
                .lt('created_at', f'{hoje} 23:59:59')\
                .execute()
            
            # Calcular estatísticas
            total_consultas = len(consultas_hoje.data)
            total_calculos = len(calculos_hoje.data)
            
            # Rating médio
            ratings = [f['rating'] for f in feedback_hoje.data]
            rating_medio = sum(ratings) / len(ratings) if ratings else 0
            
            # Artigos mais consultados
            artigos_consultados = []
            for consulta in consultas_hoje.data:
                if consulta.get('artigos_consultados'):
                    artigos_consultados.extend(consulta['artigos_consultados'])
            
            # Contar frequência dos artigos
            from collections import Counter
            artigos_freq = Counter(artigos_consultados)
            
            return {
                'data': str(hoje),
                'total_consultas': total_consultas,
                'total_calculos': total_calculos,
                'rating_medio': round(rating_medio, 2),
                'total_feedback': len(ratings),
                'artigos_mais_consultados': dict(artigos_freq.most_common(5))
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def obter_consultas_recentes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém as consultas mais recentes"""
        
        try:
            result = self.supabase.table('consultas_clt')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"Erro ao obter consultas recentes: {str(e)}")
            return []
    
    def atualizar_estatisticas_diarias(self):
        """Atualiza as estatísticas diárias"""
        
        try:
            stats = self.obter_estatisticas_hoje()
            
            if stats:
                # Tentar inserir ou atualizar
                data = {
                    'data': stats['data'],
                    'total_consultas': stats['total_consultas'],
                    'total_calculos': stats['total_calculos'],
                    'artigos_mais_consultados': json.dumps(stats['artigos_mais_consultados'])
                }
                
                # Upsert (insert ou update)
                result = self.supabase.table('estatisticas_uso')\
                    .upsert(data, on_conflict='data')\
                    .execute()
                
                return True
                
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {str(e)}")
            return False


# Instância global do gerenciador
supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Obtém instância do gerenciador Supabase"""
    global supabase_manager
    
    if supabase_manager is None:
        supabase_manager = SupabaseManager()
    
    return supabase_manager


# Funções de conveniência para usar no Parlant
async def log_consulta_clt(session_id: str, tipo: str, pergunta: str, resposta: str, 
                          artigos: List[str] = None):
    """Log de consulta para usar nas ferramentas do Parlant"""
    
    try:
        manager = get_supabase_manager()
        return manager.salvar_consulta(session_id, tipo, pergunta, resposta, artigos)
    except Exception as e:
        print(f"Erro ao fazer log da consulta: {str(e)}")
        return False


async def log_calculo_rescisao(session_id: str, salario: float, meses: int, 
                              tipo_demissao: str, resultado: Dict[str, Any]):
    """Log de cálculo de rescisão"""
    
    try:
        manager = get_supabase_manager()
        return manager.salvar_calculo_rescisao(session_id, salario, meses, tipo_demissao, resultado)
    except Exception as e:
        print(f"Erro ao fazer log do cálculo: {str(e)}")
        return False


if __name__ == "__main__":
    # Script para setup inicial
    print("🔧 Configurando Supabase para Dr. CLT...")
    
    try:
        manager = SupabaseManager()
        manager.create_tables()
        
        print("✅ Configuração do Supabase concluída!")
        print("📊 Testando conexão...")
        
        # Teste básico
        stats = manager.obter_estatisticas_hoje()
        print(f"📈 Estatísticas de hoje: {stats}")
        
    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)}")
        print("💡 Verifique se as variáveis SUPABASE_URL e SUPABASE_KEY estão configuradas")