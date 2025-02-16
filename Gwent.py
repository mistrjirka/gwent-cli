from Player import PlayerState
from Board import Board
from BoardView import BoardView
from Player import HumanController, AIController
from CardLoader import CardLoader
import random
import curses

class GwentGame:
    def __init__(self):
        # Initialize card loader once
        self.card_loader = CardLoader()
        
        # Get some random cards for testing
        all_card_ids = list(self.card_loader.get_all_card_ids())
        player_cards = random.sample(all_card_ids, 10)  # Deal 10 random cards
        ai_cards = random.sample(all_card_ids, 10)

        # Initialize the game components
        self.board = Board()
        self.view = BoardView()
        self.human = HumanController([self.card_loader.get_card_by_id(cid) for cid in player_cards])
        self.ai = AIController([self.card_loader.get_card_by_id(cid) for cid in ai_cards])
        self.is_player_turn = True
        self.running = True

    def run(self):
        try:
            self.view.init_curses()
            
            # Initial board draw
            self.view.draw_board(self.board, 0, 0, self.is_player_turn, self.human.hand)
            
            while self.running:
                try:
                    player_score = self.board.get_player_value()
                    opponent_score = self.board.get_enemy_value()
                    
                    if self.is_player_turn:
                        # Draw before getting input
                        self.view.draw_board(self.board, player_score, opponent_score, 
                                           self.is_player_turn, self.human.hand)
                        card, row = self.human.play_card(self.view)
                        if card:
                            self.board.add_card_to_row(card, True, row or "CLOSE")
                            self.view.log.append(f"Player played {card.name}")
                            self.is_player_turn = False
                    else:
                        curses.napms(1000)  # 1 second delay
                        card, row = self.ai.play_card(self.view)
                        if card:
                            self.board.add_card_to_row(card, False, row or "CLOSE")
                            self.view.log.append(f"Opponent played {card.name}")
                            self.is_player_turn = True
                    
                    # Always redraw after any action
                    self.view.draw_board(self.board, player_score, opponent_score, 
                                       self.is_player_turn, self.human.hand)
                    
                    # Check end conditions
                    if not self.human.hand and not self.ai.hand:
                        self.running = False
                        break
                    
                    # Handle input with timeout
                    self.view.stdscr.timeout(100)
                    key = self.view.stdscr.getch()
                    if key == curses.KEY_RESIZE:
                        self.view.max_y, self.max_x = self.view.stdscr.getmaxyx()
                        
                except curses.error:
                    continue
                    
        except Exception as e:
            self.view.end_curses()
            print(f"Error: {str(e)}")
        finally:
            try:
                self.view.end_curses()
            except:
                pass  # Ignore errors during cleanup
            winner = "Player" if player_score >= opponent_score else "Opponent"
            print(f"Game Over! Winner: {winner}")

if __name__ == "__main__":
    game = GwentGame()
    game.run()
