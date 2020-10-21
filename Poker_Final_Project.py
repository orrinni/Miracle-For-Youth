import random
"""Represents a single poker card."""
class Card:

    """Creates a new Instance of Card from the supplied SUIT and VALUE."""
    def __init__(self, suit, value):
        self.value = value
        self.suit = suit
        if value == 'J':
            self.power = 11
        elif value == 'Q':
            self.power = 12
        elif value == 'K':
            self.power = 13
        elif value == 'A':
            self.power = 14
        else:
            self.power = self.value 

    def __str__(self):
        if self.value == 10:
            return """-------\n|{0}    |\n|  10 |\n|    {0}|\n-------\n""".format(self.suit)
        return """-------\n|{0}    |\n|  {1}  |\n|    {0}|\n-------\n""".format(self.suit, self.value)

"""Represents a standard deck of 52 Cards."""
class Deck:
    SUITS = ["♠", "♣", "♥", "♦"]

    """Creates a new Instance of a Deck Object as a randomized list of 52 cards."""
    def __init__(self):
        self.cards = []
        for suit in Deck.SUITS:
            self.cards.append(Card(suit, 'A'))
            for val in range(2, 11):
                self.cards.append(Card(suit, val))
            self.cards.append(Card(suit, 'J'))
            self.cards.append(Card(suit, 'Q'))
            self.cards.append(Card(suit, 'K'))
        random.shuffle(self.cards)
     
    """Returns the topmost Card from the Deck."""
    def drawCard(self):
        return self.cards.pop()

    """Returns a list of the remaining cards in the Deck."""
    def getCards(self):
        return self.cards

"""Represents the Poker table and is in charge of operating each round of
betting."""
class Table:

    """Creates a new instance of a round of Poker. Begins by Showing center Cards and Dealing 2 cards to every player."""
    def __init__(self, players, big_blind):
        self.pot = 0
        self.centerCards = []
        self.deck = Deck()
        self.highest_bet = 0
        self.players = players[big_blind:] + players[0:big_blind]
        self.all_ins = []
        for player in self.players:
            player.deal(self.deck.drawCard())
            player.deal(self.deck.drawCard())

    """Main Method of Table."""
    def play(self):
        #Formatting
        print()
        print('These players are in the round!')
        player_string = ""
        for player in self.players:
            player_string += player.name + ", "
        print(player_string[:-2] + "\n")
        
        #Runs the initial round with no cards on the table
        self.betting_round()
        for player in self.players:
                player.bet = 0

        #Sets up the flop
        for _ in range(0, 3):
            self.centerCards.append(self.deck.drawCard())

        #Runs all subsequent rounds until only one person is left or 5 cards have been dealt
        while len(self.players) + len(self.all_ins) > 1 and len(self.centerCards) < 6:
            self.highest_bet = 0
            if len(self.players) > 1:
                self.betting_round()
            self.draw()
            for player in self.players:
                player.bet = 0
        
        if len(self.centerCards) > 5:
            self.centerCards.pop()

        self.settle()
        print('--------------------------------------------------------------------------------')

    """The Round itself after a new card is shown."""
    def betting_round(self):
        #Sets up blinds
        self.pot += 75
        self.players[-1].money -= 50
        self.players[-1].bet = 50
        self.players[-2].money -= 25
        self.players[-2].bet = 25
        self.highest_bet = 50
        bb = self.players[-1]

        #Goes until 1 player left or everyone is ALL IN
        while len(self.players) > 1 or (self.players and self.all_ins):
            curr_player = self.players.pop(0)

            #Checks if the turn has checked back to the original raiser
            if (curr_player.bet == self.highest_bet):
                #Only exception is for the big blind
                if not (curr_player == bb and curr_player.bet == 50): 
                    self.players.insert(0, curr_player)
                    break

            if isinstance(curr_player, Human):
                self.display_game(curr_player)

            self.pot += curr_player.move(self.highest_bet, self.centerCards)
            self.highest_bet = max(self.highest_bet, curr_player.bet)

            #Checks for all ins and folds
            if not curr_player.folded:
                if curr_player.money == 0:
                    self.all_ins.append(curr_player)
                else:
                    self.players.append(curr_player)


    """Distribute pot amongst all the winners of the finished round"""
    def settle(self):
        print('--------------------------------------------------------------------------------')
        self.players.extend(self.all_ins)

        if len(self.players) == 1:
            self.players[0].money += self.pot
            print(self.players[0].name + " won the round.")
            return
            
        winners = [self.players[0]]
        highest_score = self.players[0].heuristic(self.centerCards)
        
        for player in self.players[1:]: 
            score = player.heuristic(self.centerCards)
            holder = self.bigger_than(score, highest_score)
            if holder == 1:
                winners = [player]
            elif holder == 0:
                winners.append(player)

        print('These players won the round!')
        for winner in winners:
            winner.money += (self.pot/len(winners))
            print(winner.name)
        
    
    """Figures out the larger of two heuristic scores,"""
    def bigger_than(self, score1, score2):
        for x in range(min(len(score1), len(score2))):
            s1 = int(score1[x], 16)
            s2 = int(score2[x], 16)
            if s1 > s2:
                return 1
            elif s2 > s1:
                return 2
        
        return 0
    
    """Displays the current state of the game. The current player's cards, the round's cards and the call amount."""
    def display_game(self, curr_player):
        print(self)
        print(curr_player)


    """Returns the deck being used in the current round."""   
    def getDeck(self):
        return self.deck

    """Adds a card from the Deck to the center of the Table."""
    def draw(self):
        self.centerCards.append(self.deck.drawCard())
    
    def __str__(self):
        print('--------------------------------------------------------------------------------')
        print('The cards on the table are: ')
        result = ""
        for card in self.centerCards:
            result += str(card)
            
        result += '\nThe highest bet on the table is: ' + str(self.highest_bet)
        
        return result
        
class Game:
    """Creates a new instance of a game of Poker by creating a list of players and shuffling the order."""
    def __init__(self, com, humans):
        self.players = []
        for x in range(com):
            self.players.append(Computer(x))
        for name in humans:
            self.players.append(Human(name)) 
        random.shuffle(self.players)
        self.big_blind = self.players[0]

    """Removes players from the game that have busted and moves the Big Blind to the next available player."""
    def game_over(self):
        while True:
            index = self.players.index(self.big_blind)
            self.big_blind = self.players[(index + 1) % len(self.players)]
            if self.big_blind.money > 0:
                break
        
        #Removes losers and resets all remaining players
        place_holder = self.players[:]
        for player in place_holder:
            if player.money <= 0:
                self.players.remove(player)
            else:
                player.folded = False
                player.bet = 0
                player.hand = []

    """Play a game of Poker by continuously creating and playing new rounds until 1 player remains."""
    def play(self):
        while len(self.players) > 1:
            round = Table(self.players, self.players.index(self.big_blind))
            round.play()
            self.game_over()

        print("Player " + self.players[0].name + " has won!")    
        print("Game over!") 
        print('--------------------------------------------------------------------------------')

class Player:
    """Instantiates a Player with an empty hand, and 1000 money."""
    def __init__(self):
        self.hand = []
        self.money = 1000
        self.bet = 0
        self.folded = False

    """Adds the card CARD to this player's hand."""
    def deal(self, card):
        self.hand.append(card)

    """Returns TRUE if this player has folded in this round."""
    def hasFolded(self):
        return self.folded
    
    """Returns the value of the amount this player has bet in this round."""
    def getBet(self):
        return self.bet

    """Returns TRUE if this player is of subtype HumanPlayer."""
    def isHuman(self):
        return type(self) == Human

    """Returns a heuristic evaluation of the best hand for SELF
    in the form of a hexidecimal str. The first character will 
    always be the hand "type," with the remaining characters acting
    as tie breakers."""   
    def heuristic(self, center_cards):
        cards = self.hand[:]
        cards.extend(center_cards)
        cards.sort(key=lambda x: x.power)
        
        if len(cards) >= 5:
            if Player.royal_flush(cards):
                return "9000"
            elif Player.straight_flush(cards):
                second_digit = hex(Player.straight_flush(cards)[-1].power)[2]
                return "8" + second_digit + "00"
            elif Player.four_of_a_kind(cards):
                card = Player.four_of_a_kind(cards)
                cards = list(filter(lambda x: x.power!=card.power, cards))
                return "7" + hex(card.power)[2] + hex(cards[-1].power)[2] + "0"
            elif Player.full_house(cards):
                return Player.full_house(cards)
            elif Player.flush(cards):
                second_digit = hex(Player.flush(cards)[-1].power)[2]
                return "5" + second_digit + "00" 
            elif Player.straight(cards):
                second_digit = hex(Player.straight(cards)[-1].power)[2]
                return "4" + second_digit + "00" 
            elif Player.three_of_a_kind(cards):
                card = Player.three_of_a_kind(cards)[0]
                cards = list(filter(lambda x: x.power!=card.power, cards))
                return Player.tie_breaker("3" + hex(card.power)[2], cards, 4)
            elif Player.two_pair(cards):
                return Player.two_pair(cards)
        
        if Player.pair(cards):
            card = Player.pair(cards)[0]
            cards = list(filter(lambda x: x.power!=card.power, cards))
            return Player.tie_breaker("1" + hex(card.power)[2], cards, 5)
        else:
            return Player.tie_breaker("0", cards, 6)

    """Checks for the largest pair."""                             
    def pair(cards):
        cards = cards[:]
        for i in range(len(cards) - 1, 0, -1):
            if cards[i].power == cards[i-1].power:
                return [cards[i], cards[i-1]]
        return ""

    """Checks for the largest 3 of a kind."""
    def three_of_a_kind(cards):
        cards = cards[:]

        for i in range(len(cards) - 1, 1, -1):
            if cards[i].power == cards[i - 1].power and cards[i].power == cards[i - 2].power:
                return [cards[i], cards[i-1], cards[i-2]]
        return []

    """Checks for the largest four of a kind."""
    def four_of_a_kind(cards):
        cards = cards[:]

        for i in range(len(cards)- 3):
            if cards[i].power == cards[i + 1].power and cards[i].power == cards[i + 2].power and cards[i].power == cards[i + 3].power:
                return cards[i]
        return ""

    """Checks for the largest two pair."""
    def two_pair(cards):
        cards = cards[:]

        pairFound = False
        for i in range(len(cards) - 1):
            if cards[i].power == cards[i+1].power:
                if (pairFound is False):
                    pairFound = cards[i].power
                else:
                    pair = cards[i]
                    cards = list(filter(lambda x: x.power!=pairFound and x.power!=cards[i].power, cards))
                    return "2" + hex(pair.power)[2] + hex(pairFound)[2] + hex(cards[-1].power)[2]
        return ""

    """Checks for the largest full house."""
    def full_house(cards):
        cards = cards[:]
        trips = Player.three_of_a_kind(cards)
        
        if trips:
            for card in trips:
                cards.remove(card)
            if Player.pair(cards):
                return "6" + hex(trips[0].power)[2] + hex(Player.pair(cards)[0].power)[2] + "0"
                
        return ""
        
    """Checks for a royal flush."""
    def royal_flush(cards):
        cards = cards[:]
        straight = Player.straight(cards)
        flush = Player.flush(cards)
        if not straight or not flush:
            return False

        return straight == flush and straight[-1] == 14
        
    """Checks for a straight flush."""
    def straight_flush(cards):
        cards = cards[:]
        return Player.straight(Player.flush(cards))

    """Checks for a flush."""
    def flush(cards):
        cards = cards[:]
        cards.sort(key=lambda x: x.suit)
        
        while len(cards) > 4:
            check_list = []
            check_list.append(cards.pop(0))
            for num in range(4):
                if cards[num].suit == check_list[0].suit:
                    check_list.append(cards[num])
                else:
                    break
            if len(check_list) == 5:
                return check_list
        
        return []
    
    """Checks for the largest straight."""
    def straight(cards):
        cards = cards[:]
        cards.reverse()
        
        while len(cards) > 4:
            check_list = []
            check_list.append(cards.pop(0))
            for num in range(4):
                if cards[num].power == check_list[-1].power - 1:
                    check_list.append(cards[num])
                else:
                    break
            if len(check_list) == 5:
                return check_list
        
        return []
        
    """Fills in herisitic hex strings with tie-breaking values."""
    def tie_breaker(string, cards, length):
        cards = cards[:]
        while len(string) < length and len(cards) > 0:
            string += hex(cards[-1].power)[2]
            cards.pop()

        return string

    """Handles general betting circumstances for all players."""    
    def move(self, call_amount, center_cards):
        if isinstance(self, Human):
            bet = self.get_bet(call_amount - self.bet)
        else:
            bet = self.get_bet(call_amount - self.bet, center_cards)
        
        if self.bet + bet < call_amount:
            self.folded = True
        
        self.money = max(self.money - bet, 0)
        self.bet += bet
        return bet
        
    def __str__(self):
        print('Player: ' + self.name)
        print('Your current amount of money is: ' + str(self.money))
        print('Your current cards are: ')
        for card in self.hand:
            print(card)
        return ''
        
        

class Human(Player):

    def __init__(self, name):
        self.name = name
        super().__init__()
    
    """Handles betting input for human players."""
    def get_bet(self, call_amount):
        bet = input ("How much would you like to bet? Input 0 to FOLD or input {0} to CALL: ".format(call_amount))
        while True:
            try:
                bet = int(bet)
                if bet == self.money or bet == 0:
                    break
                if (bet < call_amount or bet > self.money):
                    bet = input ("How much would you like to bet? Input 0 to FOLD or input {0} to CALL: ".format(call_amount))
                else:
                    break
            except:
                bet = input ("How much would you like to bet? Input 0 to FOLD or input {0} to CALL: ".format(call_amount))
            
        return bet
    
    
class Computer(Player):

    def __init__(self, num):
        self.name = "Computer Player " + str(num)
        super().__init__()
    
    """Generates a bet for computer players based on a heurisitic
    evaluation of their hand."""
    def get_bet(self, call_amount, center_cards):
        bet = 0
        combined = self.hand[:]
        combined.extend(center_cards)
        heur = self.heuristic(combined)
        hand_type = int(heur[0])
        
        if hand_type >= 6:
            bet = self.money
        elif hand_type > 2:
            bet = random.randint(min(call_amount, self.money), self.money)
        elif hand_type >= 1:
            bet = min(call_amount, self.money)
        else:
            bet = 0
            
        return bet
        

    
    

print("Welcome to MFY Poker! For our version, there will be no sidepots and 'A' will only represent the highest card.")
play = True
while play == True:
    num_human = 0
    num_comp = 0
    humans = []
    while (num_human + num_comp) < 2:
        num_human = int(input('Number of human players: '))
        for i in range(num_human):
            humans.append(input(("What is the name of player {}? ").format(i+1)))
        num_comp = int(input('Number of computer players: '))
        if  (num_human + num_comp) >= 2:
            break
        else:
            print('Invalid number, try again.')  
    game = Game(num_comp, humans)
    game.play()
    again = input("If you would like to play again enter 'y'. Press any other key to quit. ")
    if again != 'y':
        play = False
