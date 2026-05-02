"""
Page: Check Rules
"""
import streamlit as st


def render():
    st.markdown("""
    <div style='text-align:center;padding:10px 0 24px;'>
        <span style='font-size:36px;'>📖</span>
        <h1 style='margin:0;font-size:1.8rem;letter-spacing:2px;'>RULES</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    > Full official rules: [bicyclecards.com/how-to-play/blackjack](https://bicyclecards.com/how-to-play/blackjack)
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Objective")
        st.markdown("""
Beat the dealer by getting a hand value **as close to 21 as possible** without going over.

- **Blackjack** = Ace + any 10-value card on the first two cards
- **Bust** = hand value exceeds 21 → you lose immediately
        """)

        st.markdown("### 🃏 Card Values")
        st.markdown("""
| Card | Value |
|------|-------|
| 2 – 9 | Face value |
| 10, J, Q, K | 10 |
| Ace | 1 or 11 (best for you) |
        """)

        st.markdown("### 💰 Payouts")
        st.markdown("""
| Outcome | Payout |
|---------|--------|
| Win | +1× bet |
| Blackjack | +1.5× bet |
| Double win | +2× bet |
| Draw | 0 (bet returned) |
| Lose | −1× bet |
| Double lose | −2× bet |
        """)

    with col2:
        st.markdown("### 🎮 Your Actions")
        st.markdown("""
**Hit** — Draw one more card.

**Stay** — Keep your current hand and let the dealer play.

**Double** *(first 2 cards only)* — Double your bet, draw exactly one card, then stay automatically.

**Split** *(first 2 cards, same value only)* — Split into two separate hands, each gets one new card. Each hand is played for the original bet.
        """)

        st.markdown("### 🏦 Dealer Rules")
        st.markdown("""
- Dealer **must hit** on 16 or less
- Dealer **must stand** on 17 or more
- Dealer's second card stays hidden until your turn is over
        """)

        st.markdown("### 🎲 This Game's Rules")
        st.markdown("""
- Single standard 52-card deck (reshuffle when exhausted)
- Starting capital: **100 🪙**
- Available bets: **5 / 10 / 15 / 50 🪙**
- Stats tracked in session (not saved between sessions)
        """)
