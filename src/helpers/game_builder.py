from config import GameResult, Rules
from helpers.deck_build import Card
from utils.turn import draw_cards, get_score, hand_str, show_table, get_player_action
from utils.turn import hit, double, split, evaluate_hand, dealer_draw


class Turn:
    @staticmethod
    def start(deck: list, pos: int) -> tuple:
        """Deal two cards each to player and house. Detect immediate Blackjacks.

        Returns: (result, deck, pos, player_hand, house_hand)
        """
        cards, deck, pos = draw_cards(deck, pos, count=Rules.START_CARDS)
        player_hand = [cards[0], cards[2]]
        house_hand = [cards[1], cards[3]]

        player_bj = get_score(player_hand) == Rules.BLACKJACK
        house_bj = get_score(house_hand) == Rules.BLACKJACK

        print("\n=== NEW GAME ===")

        if player_bj and house_bj:
            print(f"Both Blackjack — Draw!\nHouse: {hand_str(house_hand)}\nPlayer: {hand_str(player_hand)}")
            return GameResult.DRAW, deck, pos, player_hand, house_hand

        if house_bj:
            print(f"House Blackjack — you lose.\nHouse: {hand_str(house_hand)}\nPlayer: {hand_str(player_hand)} ({get_score(player_hand)})")
            return GameResult.LOSE, deck, pos, player_hand, house_hand

        if player_bj:
            print(f"Blackjack — you win!\nHouse: {house_hand[0].full_name} + Hidden\nPlayer: {hand_str(player_hand)}")
            return GameResult.WIN, deck, pos, player_hand, house_hand

        return GameResult.PROCEED, deck, pos, player_hand, house_hand

    @staticmethod
    def player(result: int, deck: list, pos: int, player_hand: list = None, house_hand: list = None, first_action: bool = True) -> tuple:
        """Handle the player's turn.

        `first_action` prevents double/split after the first decision.
        Returns: (result, deck, pos, player_hand, house_hand, action)
        where action is 'double', 'split', 'blackjack', or 'normal'.
        """
        if result != GameResult.PROCEED:
            # Blackjack detected at start — propagate with appropriate label
            action = "blackjack" if result == GameResult.WIN else "normal"
            return result, deck, pos, player_hand, house_hand, action

        show_table(player_hand, house_hand)
        action = get_player_action(player_hand)

        if action == "hit":
            result, deck, pos, player_hand, house_hand = hit(deck, pos, player_hand, house_hand)
            return result, deck, pos, player_hand, house_hand, "normal"

        if action == "double" and first_action:
            result, deck, pos, player_hand, house_hand = double(deck, pos, player_hand, house_hand)
            return result, deck, pos, player_hand, house_hand, "double"

        if action == "split" and first_action and player_hand[0].value == player_hand[1].value:
            result, deck, pos, player_hand, house_hand = split(deck, pos, player_hand, house_hand)
            return result, deck, pos, player_hand, house_hand, "split"

        if action == "stay":
            return result, deck, pos, player_hand, house_hand, "normal"

        # invalid action, re-prompt
        return Turn.player(result, deck, pos, player_hand, house_hand, first_action=False)

    @staticmethod
    def house(result: int, deck: list, pos: int, player_hand: list = None, house_hand: list = None, action: str = "normal") -> tuple:
        """Handle the dealer's turn, then evaluate the outcome.
        
        Returns: (result, deck, pos, player_hand, house_hand, action)
        'action' is passed through unchanged so main.py can use it for payout.
        """
        if result != GameResult.PROCEED:
            return result, deck, pos, player_hand, house_hand, action

        deck, pos, house_hand = dealer_draw(deck, pos, house_hand)
        final_result = evaluate_hand(player_hand, house_hand)
        return final_result, deck, pos, player_hand, house_hand, action
