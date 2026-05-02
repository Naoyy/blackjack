"""
Page: Start Game
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
import streamlit as st
from config import GameResult, Bet, Wallet
from helpers.game_builder import (
    fresh_deck, deal_start,
    player_hit, player_double, player_stay, house_play,
    start_split, split_hit, split_stay,
)
from utils.turn import get_score


# ---------------------------------------------------------------------------
# Payout
# ---------------------------------------------------------------------------

def compute_gain(result, bet, action="normal"):
    if result == GameResult.WIN:
        if action == "blackjack": return int(bet * 1.5)
        if action == "double":    return int(bet * 2.0)
        return bet
    if result == GameResult.DRAW:
        return 0
    return -int(bet * 2.0) if action == "double" else -bet


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------

def init_state():
    for k, v in {
        "capital": Wallet.STARTING_CAPITAL,
        "game_state": None,
        "bet": None,
        "phase": "betting",
        "history": [],
        "deck": None,
        "pos": 0,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Card / hand HTML helpers  (everything in one string, no orphan tags)
# ---------------------------------------------------------------------------

SUIT_COLORS = {
    "hearts ♥️": "#e63946",
    "diamonds ♦️": "#e63946",
    "spades ♠️": "#1a1a2e",
    "clubs ♣️": "#1a1a2e",
}

def _card(card, hidden=False) -> str:
    if hidden:
        return (
            '<div class="bj-card bj-card-hidden">?</div>'
        )
    color = SUIT_COLORS.get(card.suit, "#1a1a2e")
    suit  = card.suit.split()[-1]
    return (
        f'<div class="bj-card" style="color:{color};">'
        f'<span class="bj-rank">{card.name}</span>'
        f'<span class="bj-suit">{suit}</span>'
        f'</div>'
    )

def _hand_block(cards_html, label, score, label_color="rgba(255,255,255,0.55)") -> str:
    score_html = (
        f'<span class="bj-score">({score})</span>' if score is not None else ""
    )
    return (
        f'<div class="bj-hand">'
        f'<div class="bj-hand-label" style="color:{label_color};">{label}</div>'
        f'<div class="bj-cards-row">{cards_html}{score_html}</div>'
        f'</div>'
    )

_DIVIDER = '<div class="bj-divider"></div>'
_TABLE_OPEN  = '<div class="bj-table">'
_TABLE_CLOSE = '</div>'


def render_table(gs, hide_house=True):
    house_hand  = gs.get("house_hand", [])
    player_hand = gs.get("player_hand", [])

    dealer_cards = "".join(
        _card(c, hidden=(hide_house and i == 1)) for i, c in enumerate(house_hand)
    )
    dealer_block = _hand_block(
        dealer_cards, "🏦 Dealer",
        get_score(house_hand) if not hide_house else None,
    )

    if player_hand and isinstance(player_hand[0], list):
        player_block = "".join(
            _hand_block("".join(_card(c) for c in h), f"👤 Hand {i+1}", get_score(h))
            for i, h in enumerate(player_hand)
        )
    elif player_hand:
        player_block = _hand_block(
            "".join(_card(c) for c in player_hand),
            "👤 Your Hand", get_score(player_hand),
        )
    else:
        player_block = ""

    st.markdown(
        _TABLE_OPEN + dealer_block + _DIVIDER + player_block + _TABLE_CLOSE,
        unsafe_allow_html=True,
    )


def render_split_table(gs, active_hand=1):
    h1, h2 = gs["split_hand1"], gs["split_hand2"]
    dealer_cards = _card(gs["house_hand"][0]) + _card(gs["house_hand"][1], hidden=True)
    dealer_block = _hand_block(dealer_cards, "🏦 Dealer", None)

    c1 = "rgba(255,220,50,0.9)" if active_hand == 1 else "rgba(255,255,255,0.5)"
    c2 = "rgba(255,220,50,0.9)" if active_hand == 2 else "rgba(255,255,255,0.5)"
    l1 = "👤 Hand 1 ← Active" if active_hand == 1 else "👤 Hand 1"
    l2 = "👤 Hand 2 ← Active" if active_hand == 2 else "👤 Hand 2"

    b1 = _hand_block("".join(_card(c) for c in h1), l1, get_score(h1), c1)
    b2 = _hand_block("".join(_card(c) for c in h2), l2, get_score(h2), c2)

    st.markdown(
        _TABLE_OPEN + dealer_block + _DIVIDER + b1 + _DIVIDER + b2 + _TABLE_CLOSE,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Save round — single source of truth, never called twice for the same round
# ---------------------------------------------------------------------------

def save_round(gs, bet):
    """Compute gains, update capital, append to history. Returns total_gain."""
    action   = gs.get("action", "normal")
    phase    = gs.get("phase", "done")
    game_id  = str(uuid.uuid4())[:8]
    cap      = st.session_state.capital   # capital BEFORE this round

    if phase == "done_split":
        total_gain = 0
        for i, (res, hand) in enumerate(zip(gs["result"],
                                            [gs["split_hand1"], gs["split_hand2"]])):
            gain  = compute_gain(res, bet, "normal")
            total_gain += gain
            cap   = max(cap + gain, 0)
            st.session_state.history.append({
                "game_id":      game_id,
                "result":       res,
                "bet":          bet,
                "gain":         gain,
                "capital_after": cap,
                "player_hand":  [c.full_name for c in hand],
                "house_hand":   [c.full_name for c in gs["house_hand"]],
                "action":       "split",
                "hand_num":     i + 1,
            })
    else:
        gain       = compute_gain(gs["result"], bet, action)
        total_gain = gain
        cap        = max(cap + gain, 0)
        st.session_state.history.append({
            "game_id":      game_id,
            "result":       gs["result"],
            "bet":          bet,
            "gain":         gain,
            "capital_after": cap,
            "player_hand":  [c.full_name for c in gs["player_hand"]],
            "house_hand":   [c.full_name for c in gs["house_hand"]],
            "action":       action,
            "hand_num":     None,
        })

    st.session_state.capital = cap
    return total_gain


def _gain_html(total_gain, capital):
    color = "#22c55e" if total_gain > 0 else "#ef4444" if total_gain < 0 else "#f59e0b"
    sign  = "+" if total_gain >= 0 else ""
    return (
        f"<div class='bj-gain-row'>"
        f"<span style='color:{color};font-size:1.25rem;font-weight:700;'>{sign}{total_gain} 🪙</span>"
        f"<span class='bj-gain-cap'> → Capital: {capital} 🪙</span>"
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    init_state()

    st.markdown(
        "<div class='bj-header'><span class='bj-logo'>🃏</span>"
        "<h1 class='bj-title'>BLACKJACK</h1></div>",
        unsafe_allow_html=True,
    )

    capital = st.session_state.capital
    cap_color = (
        "#22c55e" if capital > Wallet.STARTING_CAPITAL
        else "#ef4444" if capital < Wallet.STARTING_CAPITAL
        else "#f59e0b"
    )
    st.markdown(
        f"<div class='bj-capital'>"
        f"<span class='bj-capital-label'>Capital </span>"
        f"<span style='color:{cap_color};'>{capital} 🪙</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # BROKE
    # -----------------------------------------------------------------------
    if capital <= 0 and st.session_state.phase == "betting":
        st.markdown(
            "<div class='bj-broke'>"
            "<span style='font-size:36px;'>💸</span>"
            "<p class='bj-broke-title'>You're broke! 🥀</p>"
            "<p class='bj-broke-sub'>Alright, I'll let you play just this once 🎁<br>"
            "100 coins added to your capital.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("💰 Accept 100 coins and continue", type="primary",
                     use_container_width=True):
            st.session_state.capital = Wallet.STARTING_CAPITAL
            st.session_state.game_state = None
            st.rerun()
        return

    # -----------------------------------------------------------------------
    # BETTING PHASE
    # -----------------------------------------------------------------------
    if st.session_state.phase == "betting":
        st.markdown(
            "<p class='bj-hint'>Place your bet to start a new round</p>",
            unsafe_allow_html=True,
        )
        affordable = [b for b in Bet.OPTIONS if b <= capital]
        cols = st.columns(len(affordable))
        for i, amount in enumerate(affordable):
            with cols[i]:
                if st.button(f"**{amount} 🪙**", key=f"bet_{amount}",
                             use_container_width=True):
                    st.session_state.bet = amount
                    if st.session_state.deck is None:
                        st.session_state.deck, st.session_state.pos = fresh_deck()
                    gs = deal_start(st.session_state.deck, st.session_state.pos)
                    st.session_state.deck  = gs["deck"]
                    st.session_state.pos   = gs["pos"]
                    st.session_state.game_state = gs
                    st.session_state.phase = "playing"
                    st.rerun()

    # -----------------------------------------------------------------------
    # PLAYING PHASE
    # -----------------------------------------------------------------------
    elif st.session_state.phase == "playing":
        gs    = st.session_state.game_state
        bet   = st.session_state.bet
        phase = gs.get("phase", "done")

        if gs.get("message"):
            st.markdown(
                f"<div class='bj-msg'>{gs['message']}</div>",
                unsafe_allow_html=True,
            )

        # ---- SPLIT phases ------------------------------------------------
        if phase in ("split_hand1", "split_hand2"):
            active = 1 if phase == "split_hand1" else 2
            render_split_table(gs, active_hand=active)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🎯 Hit", key=f"split_hit_{phase}",
                             use_container_width=True):
                    new_gs = split_hit(gs)
                    # If the bust auto-resolved to done_split, save and finish
                    if new_gs.get("phase") == "done_split":
                        st.session_state.game_state = new_gs
                        save_round(new_gs, bet)
                        st.session_state.phase = "round_over"
                    else:
                        st.session_state.game_state = new_gs
                    st.rerun()
            with c2:
                if st.button("✋ Stay", key=f"split_stay_{phase}",
                             use_container_width=True):
                    new_gs = split_stay(gs)
                    st.session_state.game_state = new_gs
                    if new_gs.get("phase") == "done_split":
                        save_round(new_gs, bet)
                        st.session_state.phase = "round_over"
                    st.rerun()

        # ---- PLAYER phase ------------------------------------------------
        elif phase == "player":
            render_table(gs, hide_house=True)
            player_hand = gs["player_hand"]
            first_two   = len(player_hand) == 2
            can_afford_double = capital >= bet * 2
            is_pair           = first_two and player_hand[0].value == player_hand[1].value
            can_double = first_two and can_afford_double
            can_split  = is_pair and can_afford_double

            actions = [("🎯 Hit", False, ""), ("✋ Stay", False, "")]
            if first_two:
                actions.append((
                    "2️⃣ Double",
                    not can_double,
                    f"Need {bet*2} 🪙 (have {capital})" if not can_double else "",
                ))
            if is_pair:
                actions.append((
                    "✂️ Split",
                    not can_split,
                    f"Need {bet*2} 🪙 (have {capital})" if not can_split else "",
                ))

            cols = st.columns(len(actions))
            for col, (label, disabled, reason) in zip(cols, actions):
                with col:
                    clicked = st.button(
                        label, key=f"act_{label}",
                        use_container_width=True,
                        disabled=disabled,
                        help=reason or None,
                    )
                    if clicked:
                        if label == "🎯 Hit":
                            new_gs = player_hit(gs)
                            if new_gs["phase"] != "done":
                                new_gs["phase"] = (
                                    "house" if get_score(new_gs["player_hand"]) == 21
                                    else "player"
                                )
                            st.session_state.game_state = new_gs
                        elif label == "✋ Stay":
                            st.session_state.game_state = house_play(player_stay(gs))
                        elif label == "2️⃣ Double":
                            new_gs = player_double(gs)
                            if new_gs["phase"] == "house":
                                new_gs = house_play(new_gs)
                            st.session_state.game_state = new_gs
                        elif label == "✂️ Split":
                            st.session_state.game_state = start_split(gs)
                        st.rerun()

        # ---- HOUSE / DONE phases  (never receives done_split) -------------
        elif phase == "house":
            st.session_state.game_state = house_play(gs)
            st.rerun()

        elif phase == "done":
            render_table(gs, hide_house=False)
            total_gain = save_round(gs, bet)
            st.markdown(_gain_html(total_gain, st.session_state.capital),
                        unsafe_allow_html=True)
            if gs.get("message"):
                st.info(gs["message"])
            st.session_state.phase = "round_over"
            st.rerun()

        # done_split is handled inline in the split buttons above;
        # if we ever land here (e.g. after a rerun), just forward to round_over
        elif phase == "done_split":
            st.session_state.phase = "round_over"
            st.rerun()

    # -----------------------------------------------------------------------
    # ROUND OVER
    # -----------------------------------------------------------------------
    elif st.session_state.phase == "round_over":
        gs = st.session_state.game_state
        render_table(gs, hide_house=False)

        history = st.session_state.history
        if history:
            last_id      = history[-1]["game_id"]
            round_rows   = [r for r in history if r["game_id"] == last_id]
            total_gain   = sum(r["gain"] for r in round_rows)
            st.markdown(
                _gain_html(total_gain, st.session_state.capital),
                unsafe_allow_html=True,
            )
            if gs.get("message"):
                st.info(gs["message"])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again", use_container_width=True, type="primary"):
                st.session_state.phase      = "betting"
                st.session_state.game_state = None
                st.session_state.bet        = None
                st.rerun()
        with c2:
            if st.button("🚪 Quit", use_container_width=True):
                st.session_state.phase      = "betting"
                st.session_state.game_state = None
                st.session_state.bet        = None
                st.rerun()
