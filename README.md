# 🏛️ Dr. CLT - Advogado Trabalhista Virtual

Um agente de IA especializado em Direito do Trabalho brasileiro, construído com [Parlant](https://parlant.io/) e baseado na CLT oficial do Senado Federal.

![Dr. CLT](https://img.shields.io/badge/Dr.%20CLT-Advogado%20Virtual-blue)
![Parlant](https://img.shields.io/badge/Powered%20by-Parlant-green)
![CLT](https://img.shields.io/badge/Baseado%20na-CLT%20Oficial-red)

## 🎯 Funcionalidades

- **📚 Consulta à CLT Oficial**: Acesso direto ao PDF oficial da Consolidação das Leis do Trabalho do Senado Federal
- **💰 Cálculo de Rescisão**: Cálculos precisos baseados na legislação vigente
- **⏰ Prazos Legais**: Verificação de prazos prescricionais e decadenciais
- **⚖️ Jurisprudência TST**: Consulta a súmulas e decisões do Tribunal Superior do Trabalho
- **🤖 Chat Inteligente**: Interface conversacional com embed para websites
- **📊 Analytics**: Integração com Supabase para armazenar consultas e estatísticas

## 🚀 Demo

Acesse a demo em: [https://seu-projeto.vercel.app](https://seu-projeto.vercel.app)

## 🛠️ Tecnologias Utilizadas

- **[Parlant](https://parlant.io/)**: Framework para agentes de IA confiáveis
- **Python**: Backend e processamento de dados
- **Supabase**: Banco de dados e analytics
- **Vercel**: Deploy e hospedagem
- **React**: Componente de chat embeddable
- **Tailwind CSS**: Estilização da landing page

## 📋 Pré-requisitos

- Python 3.9+
- Conta no [Supabase](https://supabase.com/)
- Conta no [Vercel](https://vercel.com/)
- API Key de um provedor de LLM (OpenAI, Anthropic, etc.)

## 🔧 Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/dr-clt-advogado-virtual.git
cd dr-clt-advogado-virtual
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-supabase

# LLM Provider (escolha um)
OPENAI_API_KEY=sua-chave-openai
# ou
ANTHROPIC_API_KEY=sua-chave-anthropic

# Opcional: Para desenvolvimento
PARLANT_DEBUG=true
```

### 4. Configure o Supabase

Execute o script de configuração:

```bash
python supabase_config.py
```

### 5. Execute o agente Parlant

```bash
python advogado_trabalhista.py
```

### 6. Abra a landing page

Abra o arquivo `index.html` em seu navegador ou use um servidor local:

```bash
# Com Python
python -m http.server 3000

# Com Node.js
npx serve .
```

Acesse: `http://localhost:3000`

## 🌐 Deploy no Vercel

### 1. Prepare o projeto

Certifique-se de que todos os arquivos estão commitados:

```bash
git add .
git commit -m "Setup completo do Dr. CLT"
git push origin main
```

### 2. Configure o Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em "New Project"
3. Importe seu repositório do GitHub
4. Configure as variáveis de ambiente:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY` (ou seu provedor de LLM)

### 3. Deploy

O Vercel fará o deploy automaticamente. Sua aplicação estará disponível em:
`https://seu-projeto.vercel.app`

## 📊 Configuração do Supabase

### 1. Crie um novo projeto

1. Acesse [supabase.com](https://supabase.com)
2. Crie um novo projeto
3. Anote a URL e a chave da API

### 2. Configure as tabelas

As tabelas serão criadas automaticamente quando você executar:

```bash
python supabase_config.py
```

### Tabelas criadas:

- **consultas_clt**: Armazena todas as consultas realizadas
- **calculos_rescisao**: Armazena cálculos de rescisão
- **feedback_usuarios**: Armazena feedback dos usuários
- **estatisticas_uso**: Estatísticas diárias de uso

## 🎨 Personalização

### Modificar o agente

Edite o arquivo `advogado_trabalhista.py` para:

- Adicionar novas ferramentas (tools)
- Criar novas jornadas (journeys)
- Modificar guidelines
- Adicionar novos termos ao glossário

### Personalizar a landing page

Edite o arquivo `index.html` para:

- Alterar cores e estilos
- Modificar textos e conteúdo
- Adicionar novas seções
- Personalizar o botão do chat

### Configurar o chat

No arquivo `index.html`, modifique as propriedades do `ParlantChatbox`:

```javascript
React.createElement(ParlantChatbox, {
    agentId: "dr-clt-agent",
    server: "https://sua-api.vercel.app",
    float: true,
    // Adicione mais configurações aqui
})
```

## 📈 Analytics e Monitoramento

### Dashboard do Supabase

Acesse o dashboard do Supabase para visualizar:

- Número de consultas por dia
- Artigos mais consultados
- Feedback dos usuários
- Estatísticas de uso

### Logs do Vercel

No dashboard do Vercel, você pode monitorar:

- Logs de execução
- Performance da aplicação
- Erros e exceções

## 🔒 Segurança e Compliance

### Dados dos Usuários

- Não armazenamos dados pessoais identificáveis
- IPs são hasheados para analytics
- Consultas são anonimizadas

### Limitações Legais

⚠️ **Importante**: Este é um assistente virtual para orientação geral. Para casos específicos e representação judicial, sempre consulte um advogado habilitado na OAB.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Roadmap

- [ ] Integração com mais fontes jurídicas
- [ ] Sistema de notificações por email
- [ ] Dashboard administrativo
- [ ] API pública para desenvolvedores
- [ ] Integração com WhatsApp/Telegram
- [ ] Versão mobile nativa

## 🐛 Problemas Conhecidos

- PDF parsing pode ser lento para documentos grandes
- Algumas consultas complexas podem precisar de timeout maior
- Rate limiting pode ser necessário para uso em produção

## 📞 Suporte

- 📧 Email: suporte@dr-clt.com
- 💬 Discord: [Link do servidor]
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/dr-clt-advogado-virtual/issues)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Parlant](https://parlant.io/) - Framework incrível para agentes de IA
- [Senado Federal](https://www2.senado.leg.br/) - CLT oficial em PDF
- [TST](https://www.tst.jus.br/) - Jurisprudência trabalhista
- Comunidade de desenvolvedores Python e JavaScript

---

**Desenvolvido com ❤️ para ajudar trabalhadores brasileiros a conhecerem seus direitos**

🏛️ **Dr. CLT** - Seu Advogado Trabalhista Virtual
