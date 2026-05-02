"""
Game logic adapted for Streamlit: all functions are stateless and operate on
plain data (lists, dicts) that can be stored in st.session_state.
"""
from random import shuffle
from config import GameResult, Rules
from helpers.deck_build import non_shuffled_deck
from utils.turn import (
    draw_cards, get_score, hand_str, pick,
    dealer_draw, evaluate_hand, split_cards,
)


# ---------------------------------------------------------------------------
# Deck helpers
# ---------------------------------------------------------------------------

def fresh_deck() -> tuple[list, int]:
    deck = non_shuffled_deck.copy()
    shuffle(deck)
    return deck, 0


# ---------------------------------------------------------------------------
# Game phases — each returns a new (partial) game state dict
# ---------------------------------------------------------------------------

def deal_start(deck: list, pos: int) -> dict:
    """Deal 4 cards and detect immediate blackjacks."""
    cards, deck, pos = draw_cards(deck, pos, count=Rules.START_CARDS)
    player_hand = [cards[0], cards[2]]
    house_hand = [cards[1], cards[3]]

    player_bj = get_score(player_hand) == Rules.BLACKJACK
    house_bj = get_score(house_hand) == Rules.BLACKJACK

    if player_bj and house_bj:
        return dict(
            phase="done", result=GameResult.DRAW,
            player_hand=player_hand, house_hand=house_hand,
            deck=deck, pos=pos, action="normal",
            message="Both Blackjack — Draw! 🤝",
        )
    if house_bj:
        return dict(
            phase="done", result=GameResult.LOSE,
            player_hand=player_hand, house_hand=house_hand,
            deck=deck, pos=pos, action="normal",
            message="House Blackjack — you lose. 😞",
        )
    if player_bj:
        return dict(
            phase="done", result=GameResult.WIN,
            player_hand=player_hand, house_hand=house_hand,
            deck=deck, pos=pos, action="blackjack",
            message="Blackjack — you win! 🎉",
        )

    return dict(
        phase="player", result=GameResult.PROCEED,
        player_hand=player_hand, house_hand=house_hand,
        deck=deck, pos=pos, action="normal",
        message="",
    )


def player_hit(state: dict) -> dict:
    state = dict(state)
    deck, pos, player_hand = pick(state["deck"], state["pos"], state["player_hand"])
    state.update(deck=deck, pos=pos, player_hand=player_hand)
    score = get_score(player_hand)
    if score > Rules.BLACKJACK:
        state.update(phase="done", result=GameResult.LOSE, message="BUST — you lose! 💥")
    else:
        state["message"] = f"Score: {score}"
    return state


def player_double(state: dict) -> dict:
    state = dict(state)
    deck, pos, player_hand = pick(state["deck"], state["pos"], state["player_hand"])
    state.update(deck=deck, pos=pos, player_hand=player_hand, action="double")
    if get_score(player_hand) > Rules.BLACKJACK:
        state.update(phase="done", result=GameResult.LOSE, message="BUST on double — you lose! 💥")
    else:
        state["phase"] = "house"
    return state


def player_stay(state: dict) -> dict:
    state = dict(state)
    state["phase"] = "house"
    return state


def house_play(state: dict) -> dict:
    """Dealer draws and evaluates — moves to done."""
    state = dict(state)
    deck, pos, house_hand = dealer_draw(state["deck"], state["pos"], state["house_hand"])
    result = evaluate_hand(state["player_hand"], house_hand)
    messages = {
        GameResult.WIN: "You win! 🎉",
        GameResult.LOSE: "You lose. 😞",
        GameResult.DRAW: "Draw! 🤝",
    }
    state.update(
        phase="done", result=result,
        house_hand=house_hand, deck=deck, pos=pos,
        message=messages.get(result, ""),
    )
    return state


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

def start_split(state: dict) -> dict:
    """Initiate split: create two hands, set phase to split_hand1."""
    state = dict(state)
    deck, pos, hand1, hand2 = split_cards(state["deck"], state["pos"], state["player_hand"])
    state.update(
        deck=deck, pos=pos,
        split_hand1=hand1, split_hand2=hand2,
        split_result1=None, split_result2=None,
        phase="split_hand1", action="split",
        message="Split! Playing Hand 1 first.",
    )
    return state


def split_hit(state: dict) -> dict:
    state = dict(state)
    hand_key = "split_hand1" if state["phase"] == "split_hand1" else "split_hand2"
    deck, pos, hand = pick(state["deck"], state["pos"], state[hand_key])
    state.update(deck=deck, pos=pos, **{hand_key: hand})
    if get_score(hand) > Rules.BLACKJACK:
        result_key = "split_result1" if state["phase"] == "split_hand1" else "split_result2"
        state[result_key] = GameResult.LOSE
        state["message"] = "BUST on this hand! 💥"
        # auto-advance
        if state["phase"] == "split_hand1":
            state["phase"] = "split_hand2"
            state["message"] += " Moving to Hand 2."
        else:
            state = _resolve_split(state)
    return state


def split_stay(state: dict) -> dict:
    state = dict(state)
    if state["phase"] == "split_hand1":
        state["phase"] = "split_hand2"
        state["message"] = "Hand 1 stays. Now playing Hand 2."
    else:
        state = _resolve_split(state)
    return state


def _resolve_split(state: dict) -> dict:
    deck, pos, house_hand = dealer_draw(state["deck"], state["pos"], state["house_hand"])
    r1 = state.get("split_result1") or evaluate_hand(state["split_hand1"], house_hand)
    r2 = state.get("split_result2") or evaluate_hand(state["split_hand2"], house_hand)
    state.update(
        phase="done_split",
        split_result1=r1, split_result2=r2,
        house_hand=house_hand, deck=deck, pos=pos,
        result=[r1, r2],
        player_hand=[state["split_hand1"], state["split_hand2"]],
    )
    label = {GameResult.WIN: "Win 🎉", GameResult.LOSE: "Lose 😞", GameResult.DRAW: "Draw 🤝"}
    state["message"] = f"Hand 1: {label[r1]}  |  Hand 2: {label[r2]}"
    return state
