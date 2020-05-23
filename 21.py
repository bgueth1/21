import random
from simpleimage import SimpleImage

TABLE_MIN = 10
TABLE_MAX = 100000

DECK = ["2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac", "2h", "3h", "4h", "5h", "6h",
        "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd",
        "Qd", "Kd", "Ad", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As"]

CARD_VALUE = {"2c": 2, "3c": 3, "4c": 4, "5c": 5, "6c": 6, "7c": 7, "8c": 8, "9c": 9, "Tc": 10, "Jc": 10, "Qc": 10,
              "Kc": 10, "Ac": 11, "2h": 2, "3h": 3, "4h": 4, "5h": 5, "6h": 6, "7h": 7, "8h": 8, "9h": 9, "Th": 10,
              "Jh": 10, "Qh": 10, "Kh": 10, "Ah": 11, "2d": 2, "3d": 3, "4d": 4, "5d": 5, "6d": 6, "7d": 7, "8d": 8,
              "9d": 9, "Td": 10, "Jd": 10, "Qd": 10, "Kd": 10, "Ad": 11, "2s": 2, "3s": 3, "4s": 4, "5s": 5, "6s": 6,
              "7s": 7, "8s": 8, "9s": 9, "Ts": 10, "Js": 10, "Qs": 10, "Ks": 10, "As": 11}

HOOKER_PRICE = 200


def main():
    """
    splitting cards, payout
    """
    intro()
    buyin = pay('buyin', 0)
    rebuy = 0
    balance = [buyin]
    while play_again():
        profit = game(balance)
        balance[0] += profit
        print_result(profit, balance)
        if balance[0] == 0:
            if ask_rebuy():
                rebuy = pay('rebuy', balance)
                balance[0] = rebuy
            else:
                break
    hooker_budget(balance, buyin, rebuy)


def game(balance):
    deck = []
    for card in DECK:
        deck.append(card)
    dealer_hand = []
    player_hand = []
    wager = pay('bet', balance)
    pot = [wager]
    balance[0] -= wager
    deal_cards(deck, player_hand, dealer_hand, 2)
    player_score = player_move(deck, player_hand, balance, wager, pot)
    dealer_score = dealer_move(deck, dealer_hand)
    outcome = winning(player_score, dealer_score)
    profit = payout(outcome, pot)
    return profit



def intro():
    """
    prints intro and rules & displays a prompt to start the game
    """
    print('\nWelcome! I built my own casino. With Blackjack. And Hookers.')
    image = SimpleImage('files/bender.png')
    image.show()
    print('\nFeeling lucky today?')
    print('\nRules:', '\nTable limit is $' + str(TABLE_MIN) + '/$' + str(TABLE_MAX), '\nBlackjack pays 2:1',
          '\nDealer must stand on all 17s', '\nCommands are hit (+), stand (-) and double down(dd)')


def pay(usage, balance):
    """
    pay money, types: 'buyin' and 'bet', with restrictions for balance, TABLE_MIN & MAX
    """
    while True:
        try:
            amount = int(input('\nEnter ' + usage + ' amount: $'))
        except ValueError:
            print('Please enter a valid amount.')
            continue
        break

    if usage == 'bet':
        while not balance_is_enough(balance, amount):
            print('Balance not enough. Max. bet: $', str(balance[0]))
            while True:
                try:
                    amount = int(input('\nEnter ' + usage + ' amount: $'))
                except ValueError:
                    print('Please enter a valid amount.')
                    continue
                break
        while amount < TABLE_MIN or amount > TABLE_MAX:
            if amount < TABLE_MIN:
                print('Minimum ' + usage + ' amount is $' + str(TABLE_MIN) + '.')
                amount = int(input('\nEnter ' + usage + ' amount: $'))
            if amount > TABLE_MAX:
                print('Maximum ' + usage + ' amount is $' + str(TABLE_MAX) + '.')
                amount = int(input('\nEnter ' + usage + ' amount: $'))

    if usage == 'buyin':
        while amount < TABLE_MIN:
            print('Minimum ' + usage + ' amount is $' + str(TABLE_MIN) + '.')
            amount = int(input('\nEnter ' + usage + ' amount: $'))
    return amount


def add_a_card(deck, hand):
    """
    removes random card from deck and adds it to a hand
    """
    max_index = len(deck) - 1
    index = random.randint(0, max_index)
    chosen = deck[index]
    deck.remove(chosen)
    hand.append(chosen)


def deal_cards(deck, player_hand, dealer_hand, num_cards):
    """
    remove num_cards from deck and adding them to player & dealer_hand
    """
    for i in range(num_cards):
        add_a_card(deck, player_hand)
    for i in range(num_cards):
        add_a_card(deck, dealer_hand)
    print("\nDealer Hand: ??, ", dealer_hand[0])
    print('Your hand:', ", ".join(player_hand))


def player_move(deck, hand, balance, wager, pot):
    """
    1. check for possibility to split (two equal value cards)
    2. check if player chooses to split and has enough money to do so
    3. put one of the cards into the new split_hand
    4. play the 2 hands separately
    """
    card1 = hand[0]
    card2 = hand[1]
    if card1[0] == card2[0]:
        if balance_is_enough(balance, wager):
            split_hand = ask_split(hand)
            if split_hand is not False:
                money_to_pot(balance, wager, pot)
                value1 = float(split_play(deck, hand, balance, wager, pot))
                value2 = float(split_play(deck, split_hand, balance, wager, pot))
                return [value1, value2]
    else:
        hand = hit_or_stand(deck, hand, balance, wager, pot)
        value = float(hand_value(hand))
        if is_blackjack(hand, value):
            return 21.5
        else:
            return value


def dealer_move(deck, hand):
    """
    1. get hand value
    2. check if hand is Blackjack, if yes return 21.5
    3. dealer hits until hand value == 17 or >21, then returns hand value
    """
    print('Dealer hand:', ', '.join(hand))
    value = hand_value(hand)
    if is_blackjack(hand, value):
        print('Blackjack!')
        return 21.5
    while value < 17:
        add_a_card(deck, hand)
        value = hand_value(hand)
        if value > 21:
            print('Dealer hand:', ', '.join(hand))
            print('Dealer busted!')
            return value
        print('Dealer hand:', ', '.join(hand))
    return value


def winning(player_score, dealer_score):
    if type(player_score) == list:
        score1 = player_score[0]
        score2 = player_score[1]
        outcome1 = score_compare(score1, dealer_score)
        outcome2 = score_compare(score2, dealer_score)
        return [outcome1, outcome2]
    else:
        outcome = score_compare(player_score, dealer_score)
        return outcome


def payout(outcome, pot):
    if type(outcome) == list:
        profit = 0
        for is_won in outcome:
            if is_won == 'win':
                profit += pot[0]
            if is_won == 'push':
                profit += pot[0] / 2
            if is_won == 'blackjack':
                profit += pot[0] * 3 / 2
        pot[0] = 0
        return profit
    else:
        if outcome == 'win':
            return pot[0] * 2
        elif outcome == 'push':
            return pot[0]
        elif outcome == 'blackjack':
            return pot[0] * 3
        else:
            pot[0] = 0
            return 0



def hit_or_stand(deck, hand, balance, wager, pot):
    value = hand_value(hand)
    if is_blackjack(hand, value):
        print('Blackjack!')
        return hand
    action = action_prompt()
    if action == 'dd':
        if balance_is_enough(balance, wager):
            money_to_pot(balance, wager, pot)
            add_a_card(deck, hand)
            print('Your hand:', ', '.join(hand))
            if hand_value(hand) > 21:
                print('You busted!')
            return hand
        else:
            print('You are broke. Balance not enough to double down.')
            action = action_prompt()
    while action == '+':
        add_a_card(deck, hand)
        print('Your hand:', ', '.join(hand))
        if hand_value(hand) > 21:
            print('You busted!')
            return hand
        action = action_prompt()
    if action == '-':
        return hand


def score_compare(player_score, dealer_score):
    """
    compares a player score against a dealer score and determines the outcome
    """
    if player_score == dealer_score:
        return 'push'
    elif float(player_score) == 21.5:
        return 'blackjack'
    elif int(player_score) <= 21 < int(dealer_score):
        return 'win'
    if 21 >= int(player_score) > int(dealer_score):
        return 'win'
    else:
        return False


def is_blackjack(hand, value):
    """
    checks if the first 2 cards have a value of 21
    """
    if value == 21 and len(hand) == 2:
        return True


def balance_is_enough(balance, wager):
    """
    checks if balance is high enough to place wager
    """
    if balance[0] >= wager:
        return True


def money_to_pot(balance, wager, pot):
    """
    moves money from balance into the pot
    """
    balance[0] -= wager
    pot[0] += wager


def action_prompt():
    """
    asks player to hit or stand, also accepts dd
    """
    prompt = input('\nHit (+) or stand (-)? ')
    return prompt


def ace_1_or_11(hand):
    """
    checks if there are any aces in the current hand
    """
    aces = ("As", "Ah", "Ac", "Ad")
    if any(c in hand for c in aces):
        return True

def num_of_aces(hand):
    first = hand.count("As")
    second = hand.count("Ad")
    third = hand.count("Ah")
    fourth = hand.count("Ac")
    return first + second + third + fourth

def hand_value(hand):
    """
    returns the value sum of all cards in a hand, subtracts 10 for each if value over 21
    """
    value = 0
    for i in range(len(hand)):
        value += int(CARD_VALUE[hand[i]])
    if value > 21 and ace_1_or_11(hand):
        value -= 10 * num_of_aces(hand)
    return value


def play_again():
    """
    asks user if he wants to keep playing
    """
    prompt = input('\nPress ENTER to play, type "quit" to quit: ')
    while prompt != '' and prompt != 'quit':
        prompt = input('Press ENTER to play, type "quit" to quit: ')
    if prompt == '':
        return True
    elif prompt == 'quit':
        return False


def print_result(profit, balance):
    if profit == 0:
        print('You lost.')
        print('Your balance is now $' + str(balance[0]))
    else:
        print('You won $' + str(profit))
        print('Your balance is now $' + str(balance[0]))


def ask_rebuy():
    prompt = input('Do you want to re-buy? (y/n): ')
    while prompt != 'y' and 'n':
        prompt = input('Do you want to re-buy? (y/n): ')
    if prompt == 'y':
        return True
    if prompt == 'n':
        return False


def hooker_budget(balance, buyin_amount, rebuy_amount):
    print('Thank you for playing!')
    total = balance[0] - (buyin_amount + rebuy_amount)
    hooker_calc = balance[0] // HOOKER_PRICE
    if total < 0:
        print('\nToday you lost $' + str(total * -1))
        print('Your remaining balance is $' + str(balance[0]))
        if balance[0] < HOOKER_PRICE:
            print('You cannot afford any hookers tonight')
        else:
            print('You can still afford ' + str(hooker_calc) + ' hookers!')
    else:
        print('\nToday you won $' + str(total))
        print('Your remaining balance is $' + str(balance[0]))
        print('You can afford ' + str(hooker_calc) + ' hookers!')

def ask_split(hand) :
    """
    asks user if he wants to split his hand; if yes, creates a second hand and moves a card there
    """
    split_true = input('Do you want to split? (y/n): ')
    while split_true != 'y' and 'n':
        split_true = input('Do you want to split? (y/n): ')
    if split_true == 'y':
        split_hand = [hand[1]]
        hand.pop()
        return split_hand
    else:
        return False


def split_play(deck, hand, balance, wager, pot):
    """
    same as player_move(), but over 2 separate hands in the split scenario
    """
    add_a_card(deck, hand)
    print('\nYour hand:', ', '.join(hand))
    hand = hit_or_stand(deck, hand, balance, wager, pot)
    value = hand_value(hand)
    return value


if __name__ == '__main__':
    main()
