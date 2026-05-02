"""
Page: Check Stats
"""
import streamlit as st
from config import GameResult, Wallet
from collections import Counter


def _win_streak(history):
    """Return the longest consecutive WIN streak across all rounds (by game_id order)."""
    # Group by game_id to treat a split (2 entries) as one game
    seen = {}
    ordered_ids = []
    for r in history:
        gid = r["game_id"]
        if gid not in seen:
            seen[gid] = []
            ordered_ids.append(gid)
        seen[gid].append(r["result"])

    best, current = 0, 0
    for gid in ordered_ids:
        results = seen[gid]
        # A game is a WIN only if ALL hands won (handles split)
        if all(r == GameResult.WIN for r in results):
            current += 1
            best = max(best, current)
        elif any(r == GameResult.LOSE for r in results):
            current = 0
        # DRAW doesn't break streak, doesn't extend it
    return best


def render():
    st.markdown(
        "<div style='text-align:center;padding:10px 0 24px;'>"
        "<span style='font-size:36px;'>📊</span>"
        "<h1 style='margin:0;font-size:1.8rem;letter-spacing:2px;'>STATS</h1>"
        "</div>",
        unsafe_allow_html=True,
    )

    history = st.session_state.get("history", [])

    if not history:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;color:#888;'>"
            "<span style='font-size:48px;'>🎲</span>"
            "<p style='font-size:1.1rem;margin-top:12px;'>No stats yet — play at least one round first!</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    capital = st.session_state.get("capital", Wallet.STARTING_CAPITAL)
    total_gain = sum(r["gain"] for r in history)

    # Count unique games (a split = 1 game with 2 entries)
    unique_games = len({r["game_id"] for r in history})

    decisive = [r for r in history if r["result"] in (GameResult.WIN, GameResult.LOSE)]
    wins = [r for r in decisive if r["result"] == GameResult.WIN]
    win_rate = len(wins) / len(decisive) if decisive else 0.0
    best_streak = _win_streak(history)

    # ---- KPI cards ----
    gain_color = "#22c55e" if total_gain >= 0 else "#ef4444"
    cap_color = "#22c55e" if capital > Wallet.STARTING_CAPITAL else "#ef4444" if capital < Wallet.STARTING_CAPITAL else "#f59e0b"

    def kpi(col, label, value, color="#ffffff"):
        with col:
            st.markdown(
                f"<div style='background:#1a1a2e;border-radius:10px;padding:16px 12px;"
                f"text-align:center;border:1px solid #2a2a4a;'>"
                f"<div style='font-size:11px;color:#888;letter-spacing:1px;"
                f"text-transform:uppercase;margin-bottom:6px;'>{label}</div>"
                f"<div style='font-size:1.5rem;font-weight:700;color:{color};'>{value}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Win Rate", f"{win_rate:.1%}", "#22c55e" if win_rate >= 0.5 else "#ef4444")
    kpi(c2, "Games Played", str(unique_games), "#f59e0b")
    kpi(c3, "Best Streak", f"🔥 {best_streak}", "#f97316" if best_streak >= 3 else "#f59e0b")
    kpi(c4, "Total Gain", f"{'+' if total_gain >= 0 else ''}{total_gain} 🪙", gain_color)
    kpi(c5, "Capital", f"{capital} 🪙", cap_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Results breakdown + Actions ----
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🏆 Results Breakdown")
        losses = len(decisive) - len(wins)
        draws = len([r for r in history if r["result"] == GameResult.DRAW])
        total = len(history)

        for label, count, bar_color in [
            ("✅ Wins", len(wins), "#22c55e"),
            ("❌ Losses", losses, "#ef4444"),
            ("🤝 Draws", draws, "#f59e0b"),
        ]:
            pct = count / total if total else 0
            st.markdown(
                f"<div style='margin:6px 0;'>"
                f"<div style='display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:2px;'>"
                f"<span>{label}</span><span style='color:#aaa;'>{count}</span></div>"
                f"<div style='background:#1a1a2e;border-radius:4px;height:8px;'>"
                f"<div style='background:{bar_color};height:8px;border-radius:4px;width:{pct*100:.1f}%;'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown("#### 🎮 Actions Used")
        action_counts = Counter(r.get("action", "normal") for r in history)
        icons = {"normal": "🎯", "blackjack": "🃏", "double": "2️⃣", "split": "✂️"}
        for action, count in action_counts.most_common():
            icon = icons.get(action, "🎮")
            st.markdown(f"**{icon} {action.title()}**: {count}")

    st.markdown("---")

    # ---- Full history table ----
    st.markdown("#### 🕒 Round History")

    import pandas as pd
    result_labels = {GameResult.WIN: "✅ Win", GameResult.LOSE: "❌ Lose", GameResult.DRAW: "🤝 Draw"}

    rows = []
    for r in reversed(history):
        hand_label = f" (hand {r['hand_num']})" if r.get("hand_num") else ""
        gain_sign = "+" if r["gain"] >= 0 else ""
        rows.append({
            "Game ID": r["game_id"],
            "Result": result_labels.get(r["result"], "?") + hand_label,
            "Action": icons.get(r.get("action", "normal"), "🎮") + " " + r.get("action", "normal").title(),
            "Bet 🪙": r["bet"],
            "Gain 🪙": f"{gain_sign}{r['gain']}",
            "Capital After 🪙": r.get("capital_after", "—"),
            "Your Hand": ", ".join(r["player_hand"]),
            "Dealer Hand": ", ".join(r["house_hand"]),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---- Reset ----
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Reset Stats & Capital", type="secondary"):
        st.session_state.history = []
        st.session_state.capital = Wallet.STARTING_CAPITAL
        st.session_state.phase = "betting"
        st.session_state.game_state = None
        st.session_state.bet = None
        st.rerun()
