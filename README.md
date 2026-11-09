## 🧠 Arquitetura e Lógica Utilizada

O *DashCryptoStox* foi desenvolvido em *Python + Streamlit* com foco em integração de dados financeiros, resiliência a falhas externas e experiência de uso.

1. *Estratégia Multi-API*
   - *Ações globais:* integração com a *Alpha Vantage* por meio de tickers e séries temporais diárias.
   - *Criptomoedas:* consumo das APIs *CoinGecko* e *CoinCap* para obtenção de preços e variações de mercado.

2. *Fallback e Resiliência*
   - Caso uma API esteja indisponível ou atinja limites de requisição, a aplicação utiliza mecanismos de contingência para evitar interrupções.
   - Para ações, podem ser usados valores estáticos de referência.
   - Para gráficos, quando não há histórico disponível, é gerada uma série temporal *simulada apenas para demonstração da interface*, sem representar cotações reais.

3. *Interface Customizada*
   - Personalização do Streamlit com CSS via st.markdown.
   - Uso de paleta em tons de azul escuro e ciano para manter consistência visual em cards, inputs, seletores e gráficos.

4. *Gestão de Estado*
   - Uso do st.session_state para manter ativos monitorados e últimos valores conhecidos durante a sessão.
   - Uso de cache temporário para reduzir chamadas repetidas às APIs e melhorar a experiência da aplicação.