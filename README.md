## 🧠 Arquitetura e Lógica Utilizada

O **DashCryptoStox** foi projetado seguindo padrões de robustez e engenharia de software para garantir resiliência a falhas de APIs externas e uma excelente experiência de utilizador:

1. **Estratégia de Dados Híbrida (Multi-API):**
   * **Ações Globais (NYSE/NASDAQ):** Integração com a API da **Alpha Vantage** através de mapeamento de tickers e séries temporais diárias (`TimeSeries`).
   * **Criptomoedas:** Consumo de endpoints de mercado em tempo real da **CoinGecko** e **CoinCap**.

2. **Mecanismo Avançado de Fallback (Resiliência):**
   * As APIs financeiras gratuitas possuem limites rígidos de requisições (*rate limits*). Para evitar que a aplicação quebre ou fique presa em estados de carregamento infinito, implementou-se um sistema duplo de segurança para garantir a continuidade da experiência do utilizador durante indisponibilidades ou limitações:
     * **Valores Estáticos de Contingência:** Preços de referência calibrados para os ativos principais.
     * **Geração Estocástica de Histórico:** Caso a API falhe ou atinja o limite, o sistema gera dinamicamente uma série temporal realista baseada no preço atual, permitindo que os gráficos e seletores de período (**24h, 7D, 1M, 1A**) continuem a funcionar perfeitamente.

3. **Design System Customizado (UI/UX):**
   * Sobrescrita total dos estilos nativos do Streamlit via injeção de CSS (`st.markdown`).
   * Aplicação de uma paleta de cores moderna em tons de azul petróleo escuro (`#132238`, `#1e293b`) com destaque visual em ciano (`#38bdf8`), eliminando todos os elementos brancos padrão em inputs e seletores.

4. **Gestão de Estado Reativa:**
   * Utilização intensiva do `st.session_state` do Streamlit para persistir a lista de ativos monitorizados (`tracked_assets`), cache de preços e preferências de moedas (`USD` / `BRL`) sem perder o contexto durante as interações.