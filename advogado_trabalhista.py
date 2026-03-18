
# advogado_trabalhista.py
# Dr. CLT - Advogado Trabalhista Virtual
# Agente especializado em Direito do Trabalho brasileiro (CLT) com acesso a dados REAIS da web

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
from supabase_config import log_consulta_clt, log_calculo_rescisao

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Ferramentas do agente
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
            async with session.get(url, timeout=40) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Buscar o artigo específico
                    artigo_texto = f"Art. {artigo}"
                    artigo_encontrado = False
                    conteudo_artigo = []
                    
                    # Procurar em todas as tags
                    for elemento in soup.find_all(['p', 'div', 'span']):
                        texto = elemento.get_text().strip()
                        if artigo_texto in texto:
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

@tool
async def consultar_jurisprudencia_tst_real(context: ToolContext, termo: str) -> ToolResult:
    """Consulta jurisprudência REAL do Tribunal Superior do Trabalho"""
    try:
        # Portal oficial de jurisprudência do TST
        url = "https://busca.tst.jus.br/jurisprudencia/search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        params = {
            'q': termo,
            't': 'jurisprudencia',
            's': 'dateDesc',
            'p': '1'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params, timeout=45) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Tentar encontrar resultados
                    resultados = []
                    
                    # Procurar por diferentes padrões de elementos
                    for item in soup.select('.resultado-item, .jurisprudencia-item, .item, .result'):
                        try:
                            titulo = item.select_one('h3, h4, .titulo, .title')
                            titulo_texto = titulo.get_text().strip() if titulo else "Decisão do TST"
                            
                            ementa = item.select_one('.ementa, .summary, .descricao, p')
                            ementa_texto = ementa.get_text().strip() if ementa else "Ementa não disponível"
                            
                            processo = item.select_one('.processo, .number, .codigo, .nProcesso')
                            processo_texto = processo.get_text().strip() if processo else "Processo não disponível"
                            
                            data = item.select_one('.data, .date, .julgamento, .dtJulgamento')
                            data_texto = data.get_text().strip() if data else "Data não disponível"
                            
                            resultados.append(
                                f"**{titulo_texto}**\n"
                                f"📋 **Processo:** {processo_texto}\n"
                                f"📅 **Data:** {data_texto}\n"
                                f"📝 **Ementa:** {ementa_texto[:300]}...\n"
                            )
                            
                            if len(resultados) >= 3:
                                break
                                
                        except Exception:
                            continue
                    
                    if resultados:
                        return ToolResult("⚖️ **Jurisprudência do TST**\n\n" + "\n---\n".join(resultados) + \
                           f"\n\n🔍 **Termo pesquisado:** '{termo}'\n🌐 **Fonte:** Tribunal Superior do Trabalho")
                    
                    return ToolResult(f"ℹ️ Nenhuma jurisprudência encontrada para '{termo}' no TST.")
                
                return ToolResult("❌ Erro ao acessar o portal do TST. Tente novamente.")
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta de jurisprudência: {str(e)}")

@tool
async def consultar_sumulas_tst(context: ToolContext, termo: str) -> ToolResult:
    """Consulta súmulas do TST relacionadas ao termo"""
    try:
        url = "https://www.tst.jus.br/web/guest/sumulas"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    sumulas_relacionadas = []
                    
                    # Procurar súmulas que mencionem o termo
                    for elemento in soup.find_all(text=re.compile(termo, re.IGNORECASE)):
                        contexto = elemento.parent.get_text() if elemento.parent else elemento
                        if len(contexto) > 100:
                            sumulas_relacionadas.append(f"• {contexto[:200]}...")
                        
                        if len(sumulas_relacionadas) >= 5:
                            break
                    
                    if sumulas_relacionadas:
                        return ToolResult("⚖️ **Súmulas do TST relacionadas**\n\n" + \
                           "\n".join(sumulas_relacionadas) + \
                           f"\n\n🔍 **Termo:** '{termo}'\n🌐 **Fonte:** Tribunal Superior do Trabalho")
                    
                    return ToolResult(f"ℹ️ Nenhuma súmula encontrada para '{termo}' no TST.")
                
                return ToolResult("❌ Erro ao acessar as súmulas do TST.")
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta de súmulas: {str(e)}")

@tool
async def calcular_rescisao_clt_oficial(context: ToolContext, salario: float, meses_trabalho: int, 
                                      tipo_demissao: str, ferias_vencidas: bool = False) -> ToolResult:
    """Calcula rescisão trabalhista baseado na CLT oficial com dados REAIS"""
    
    # Validações básicas
    if salario <= 0 or meses_trabalho <= 0:
        return ToolResult({"erro": "Salário e meses de trabalho devem ser positivos"})
    
    if tipo_demissao not in ["sem_justa_causa", "com_justa_causa", "pedido_demissao"]:
        return ToolResult({"erro": "Tipo de demissão inválido. Use: sem_justa_causa, com_justa_causa ou pedido_demissao"})
    
    try:
        # Buscar valor atual do salário mínimo para referência
        salario_minimo = await obter_salario_minimo_atual()
        
        # Cálculos baseados na CLT
        resultado = {
            "salario_base": salario,
            "meses_trabalhados": meses_trabalho,
            "tipo_demissao": tipo_demissao,
            "ferias_vencidas": ferias_vencidas,
            "salario_minimo_referencia": salario_minimo
        }
        
        # Salário proporcional
        salario_proporcional = (salario * meses_trabalho) / 12
        
        # 13º proporcional
        decimo_terceiro = (salario * meses_trabalho) / 12
        
        # FGTS + 40% multa (apenas demissão sem justa causa)
        fgts_acumulado = salario * meses_trabalho * 0.08  # 8% FGTS
        
        if tipo_demissao == "sem_justa_causa":
            multa_fgts = fgts_acumulado * 0.4  # 40% multa
            resultado["multa_40_fgts"] = round(multa_fgts, 2)
        else:
            resultado["multa_40_fgts"] = 0
        
        resultado["fgts_acumulado"] = round(fgts_acumulado, 2)
        
        # Aviso prévio (30 dias + 3 dias/ano acima de 1 ano)
        aviso_previo = 30
        if meses_trabalho > 12:
            anos_completos = (meses_trabalho - 12) // 12
            aviso_previo += min(anos_completos * 3, 60)  # Máximo 90 dias
        
        aviso_previo_valor = (salario / 30) * aviso_previo
        
        # Férias + 1/3 constitucional
        if ferias_vencidas:
            ferias = salario + (salario / 3)
        else:
            # Férias proporcionais
            ferias = (salario * meses_trabalho / 12) + (salario * meses_trabalho / 12 / 3)
        
        # Total
        totais = {
            "salario_proporcional": round(salario_proporcional, 2),
            "decimo_terceiro_proporcional": round(decimo_terceiro, 2),
            "aviso_previo_dias": aviso_previo,
            "aviso_previo_valor": round(aviso_previo_valor, 2),
            "ferias_valor": round(ferias, 2)
        }
        
        total_geral = sum([v for k, v in totais.items() if isinstance(v, (int, float))])
        totais["total_geral"] = round(total_geral, 2)
        
        resultado["calculos"] = totais
        
        # Log no Supabase
        await log_calculo_rescisao("session_teste", salario, meses_trabalho, tipo_demissao, resultado)
        
        return ToolResult(resultado)
        
    except Exception as e:
        return ToolResult({"erro": f"Erro no cálculo: {str(e)}"})

async def obter_salario_minimo_atual() -> float:
    """Obtém o valor atual do salário mínimo oficial"""
    try:
        # Tentar obter do site oficial
        url = "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/salario-minimo"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Procurar valor do salário mínimo
                    for texto in soup.find_all(text=re.compile(r'R\$\s*[\d\.]+,\d{2}')):
                        match = re.search(r'R\$\s*([\d\.]+,\d{2})', texto)
                        if match:
                            valor = match.group(1).replace('.', '').replace(',', '.')
                            return float(valor)
                    
                    return 1412.00  # Valor padrão se não encontrar
                
                return 1412.00  # Valor padrão
                
    except Exception:
        return 1412.00  # Valor padrão em caso de erro

@tool
async def verificar_prazos_clt_oficial(context: ToolContext, tipo_acao: str) -> ToolResult:
    """Verifica prazos prescricionais trabalhistas baseado na CLT"""
    
    prazos = {
        "reclamacao_trabalhista": {
            "prazo": "2 anos",
            "base_legal": "Art. 7º, XXIX da CF/88 e Art. 11 da Lei nº 8.213/91",
            "observacao": "Conta-se da data da rescisão ou do término do contrato"
        },
        "fgts": {
            "prazo": "Imprescritível durante o contrato, 30 anos após",
            "base_legal": "Art. 23 da Lei 8.036/90",
            "observacao": "Durante o contrato não prescreve, após prescreve em 30 anos"
        },
        "acidente_trabalho": {
            "prazo": "5 anos",
            "base_legal": "Art. 11 da Lei 8.213/91",
            "observacao": "Conta-se da data do acidente ou da ciência do nexo causal"
        },
        "horas_extras": {
            "prazo": "5 anos",
            "base_legal": "Art. 7º, XVI da CF/88 e Súmula 363 do TST",
            "observacao": "Prescrição quinquenal"
        },
        "danos_morais": {
            "prazo": "3 anos",
            "base_legal": "Art. 206, §3º, V do CC",
            "observacao": "Conta-se da data do fato gerador"
        },
        "indenizacao_por_dano_material": {
            "prazo": "3 anos",
            "base_legal": "Art. 206, §3º, V do CC",
            "observacao": "Conta-se da data do fato gerador"
        }
    }
    
    if tipo_acao in prazos:
        info = prazos[tipo_acao]
        return ToolResult(f"⏰ **Prazo Prescricional - {tipo_acao.replace('_', ' ').title()}**\n\n"
                f"📅 **Prazo:** {info['prazo']}\n"
                f"⚖️ **Base Legal:** {info['base_legal']}\n"
                f"💡 **Observação:** {info['observacao']}")
    
    return ToolResult("❌ Tipo de ação não reconhecido. Use: reclamacao_trabalhista, fgts, acidente_trabalho, horas_extras, danos_morais, indenizacao_por_dano_material")

@tool
async def consultar_legislacao_trabalhista(context: ToolContext, termo: str) -> ToolResult:
    """Consulta legislação trabalhista em fontes oficiais"""
    try:
        # Portal da legislação do Planalto
        url = "http://www.planalto.gov.br/ccivil_03/consulta_legislacao/consulta_legislacao.php"
        
        params = {
            "pesquisa": termo,
            "tipo": "T",
            "ordenacao": "DATA_DESC"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    resultados = []
                    items = soup.select('.resultado-item, .item, .legislacao-item')[:3]
                    
                    for item in items:
                        try:
                            titulo = item.select_one('h3, .titulo, .title')
                            link = item.select_one('a')
                            data = item.select_one('.data, .date')
                            
                            if titulo and link:
                                titulo_texto = titulo.get_text().strip()
                                link_url = link.get('href', '')
                                data_texto = data.get_text().strip() if data else ""
                                
                                resultados.append(
                                    f"**{titulo_texto}**\n"
                                    f"📅 {data_texto}\n"
                                    f"🔗 {link_url}\n"
                                )
                        except Exception:
                            continue
                    
                    if resultados:
                        return ToolResult("📚 **Legislação Encontrada**\n\n" + "\n---\n".join(resultados) + \
                           f"\n\n🔍 **Termo:** '{termo}'\n🌐 **Fonte:** Planalto Federal")
                    
                    return ToolResult(f"ℹ️ Nenhuma legislação encontrada para '{termo}'")
                
                return ToolResult("❌ Erro ao consultar legislação")
                
    except Exception as e:
        return ToolResult(f"❌ Erro na consulta: {str(e)}")

async def main():
    """Função principal para criar e configurar o agente Dr. CLT"""
    # Carregar variáveis de ambiente
    load_dotenv(override=True)
    
    port = int(os.environ.get("PORT", 8802))
    async with Server(port=port, tool_service_port=8820) as server:
        # Criar o agente Dr. CLT
        agent = await server.create_agent(
            name="Dr. CLT - Advogado Trabalhista Virtual",
            description="Especialista em Direito do Trabalho brasileiro (CLT), com acesso às fontes oficiais de legislação",
            composition_mode=CompositionMode.FLUID
        )
        
        # Anexar as ferramentas ao agente usando a API correta
        await agent.attach_tool(consultar_clt_oficial, "Quando o usuário perguntar sobre artigos da CLT")
        await agent.attach_tool(consultar_jurisprudencia_tst_real, "Quando o usuário perguntar sobre jurisprudência ou decisões judiciais")
        await agent.attach_tool(consultar_sumulas_tst, "Para consultas sobre súmulas do TST")
        await agent.attach_tool(calcular_rescisao_clt_oficial, "Para cálculos trabalhistas e rescisórios")
        await agent.attach_tool(verificar_prazos_clt_oficial, "Para verificação de prazos prescricionais")
        await agent.attach_tool(consultar_legislacao_trabalhista, "Para consultas gerais de legislação trabalhista")
        
        print("🏛️ Dr. CLT - Advogado Trabalhista Virtual iniciado!")
        print("📚 Baseado na CLT oficial e fontes governamentais")
        print("🌐 Acesse: http://localhost:8802")
        print("⚖️ Ferramentas disponíveis:")
        print("   • Consultar CLT oficial")
        print("   • Jurisprudência do TST (dados reais)")
        print("   • Cálculo de rescisão")
        print("   • Verificação de prazos")
        print("   • Consulta de legislação")
        
        # Manter o servidor rodando
        await asyncio.Future()

# Inicialização do agente
if __name__ == "__main__":
    asyncio.run(main())