# 🧪 Guia de Teste - Dr. CLT

Este guia te ajudará a testar todas as funcionalidades do Dr. CLT antes do deploy em produção.

## 🚀 Teste Local

### 1. Preparação do Ambiente

```bash
# Clone e configure
git clone <seu-repositorio>
cd dr-clt-advogado-virtual

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves
```

### 2. Teste do Supabase

```bash
# Configure as tabelas
python supabase_config.py
```

**Resultado esperado:**
```
🔧 Configurando Supabase para Dr. CLT...
✅ Tabelas criadas com sucesso no Supabase
✅ Configuração do Supabase concluída!
📊 Testando conexão...
📈 Estatísticas de hoje: {...}
```

### 3. Teste do Agente Parlant

```bash
# Execute o agente
python advogado_trabalhista.py
```

**Resultado esperado:**
```
🏛️ Dr. CLT - Advogado Trabalhista Virtual iniciado!
📚 Baseado na CLT oficial do Senado Federal
🌐 Acesse: http://localhost:8800
⚖️ Consulte artigos da CLT, calcule rescisões e verifique prazos!
```

### 4. Teste da Landing Page

```bash
# Servidor local
python -m http.server 3000
```

Acesse: `http://localhost:3000`

**Verificar:**
- ✅ Página carrega corretamente
- ✅ Botão de chat aparece no canto inferior direito
- ✅ Design responsivo funciona
- ✅ Todas as seções estão visíveis

## 🤖 Teste das Funcionalidades do Chat

### 1. Consulta à CLT

**Teste:** Digite no chat: "Consulte o artigo 477 da CLT"

**Resultado esperado:**
- Ferramenta `consultar_clt_senado` é chamada
- Retorna texto do artigo 477 sobre rescisão
- Fonte: CLT - Senado Federal

### 2. Cálculo de Rescisão

**Teste:** Digite: "Quero calcular minha rescisão"

**Dados de teste:**
- Salário: R$ 3.000,00
- Tempo de serviço: 24 meses
- Tipo: Demissão sem justa causa

**Resultado esperado:**
- Ferramenta `calcular_rescisao_clt_oficial` é chamada
- Retorna cálculo detalhado com base legal
- Inclui FGTS, aviso prévio, férias, 13º

### 3. Consulta de Prazos

**Teste:** Digite: "Qual o prazo para cobrar FGTS?"

**Resultado esperado:**
- Ferramenta `verificar_prazos_clt_oficial` é chamada
- Retorna: "Imprescritível durante o contrato"
- Base legal: CF/88, Art. 7º, XXIX

### 4. Jurisprudência TST

**Teste:** Digite: "Busque jurisprudência sobre horas extras"

**Resultado esperado:**
- Ferramenta `consultar_jurisprudencia_tst` é chamada
- Retorna súmulas ou decisões relacionadas
- Fonte: TST

## 📊 Teste do Supabase

### Verificar Logs

Após os testes acima, verifique no dashboard do Supabase:

1. **Tabela `consultas_clt`**: Deve ter registros das consultas
2. **Tabela `calculos_rescisao`**: Deve ter o cálculo realizado
3. **Tabela `estatisticas_uso`**: Deve mostrar estatísticas do dia

### Teste Manual de Inserção

```python
# Execute no Python
from supabase_config import get_supabase_manager

manager = get_supabase_manager()
result = manager.salvar_consulta(
    session_id="teste-123",
    tipo_consulta="teste",
    pergunta="Teste de inserção",
    resposta="Teste funcionando"
)
print(f"Inserção: {result}")
```

## 🌐 Teste de Deploy (Vercel)

### 1. Deploy de Teste

```bash
# Commit e push
git add .
git commit -m "Versão para teste"
git push origin main

# Deploy no Vercel
vercel --prod
```

### 2. Verificações Pós-Deploy

**URL de produção:** `https://seu-projeto.vercel.app`

**Checklist:**
- ✅ Landing page carrega
- ✅ Chat funciona
- ✅ Consultas à CLT funcionam
- ✅ Cálculos funcionam
- ✅ Logs no Supabase funcionam
- ✅ Performance adequada (< 3s)

### 3. Teste de Carga

Use ferramentas como:
- [GTmetrix](https://gtmetrix.com/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [WebPageTest](https://www.webpagetest.org/)

**Métricas esperadas:**
- Performance Score: > 80
- First Contentful Paint: < 2s
- Largest Contentful Paint: < 3s

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão Supabase
```
Erro: SUPABASE_URL e SUPABASE_KEY devem estar configuradas
```
**Solução:** Verifique o arquivo `.env` e as variáveis no Vercel

#### 2. Erro de PDF Parsing
```
Erro ao consultar CLT do Senado: timeout
```
**Solução:** Aumente o timeout ou use cache local

#### 3. Chat não aparece
**Solução:** 
- Verifique se o servidor Parlant está rodando
- Confirme a URL no `index.html`
- Verifique console do navegador

#### 4. Cálculos incorretos
**Solução:**
- Verifique fórmulas na função `calcular_rescisao_clt_oficial`
- Confirme valores de salário mínimo atualizados

### Logs Úteis

#### Vercel
```bash
vercel logs https://seu-projeto.vercel.app
```

#### Supabase
- Dashboard > Logs
- Filtrar por tabela e timestamp

#### Parlant
- Logs aparecem no terminal onde rodou o agente
- Use `PARLANT_DEBUG=true` para mais detalhes

## ✅ Checklist Final

Antes de considerar o projeto pronto:

### Funcionalidades
- [ ] Consulta à CLT funciona
- [ ] Cálculo de rescisão funciona
- [ ] Consulta de prazos funciona
- [ ] Jurisprudência TST funciona
- [ ] Chat embed funciona
- [ ] Logs no Supabase funcionam

### Performance
- [ ] Página carrega em < 3s
- [ ] Chat responde em < 10s
- [ ] PDF parsing funciona (pode ser lento)
- [ ] Sem erros no console

### Deploy
- [ ] Vercel deploy funciona
- [ ] Variáveis de ambiente configuradas
- [ ] HTTPS funcionando
- [ ] Domain personalizado (opcional)

### Documentação
- [ ] README.md completo
- [ ] .env.example atualizado
- [ ] Comentários no código
- [ ] Este guia de teste

## 🎉 Próximos Passos

Após todos os testes passarem:

1. **Monitoramento**: Configure alertas no Vercel e Supabase
2. **Analytics**: Implemente Google Analytics (opcional)
3. **SEO**: Otimize meta tags e estrutura
4. **Marketing**: Compartilhe com a comunidade jurídica
5. **Feedback**: Colete feedback dos usuários
6. **Iteração**: Melhore baseado no uso real

---

**Boa sorte com o Dr. CLT! 🏛️⚖️**