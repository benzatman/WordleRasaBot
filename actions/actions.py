from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
import pickle


def load_words_pkl():
    with open('possible_words.pkl', 'rb') as f:
        words = pickle.load(f)
    words = words['words']
    return words


def letter_score(letter):
    # these scores are based on how often each letter is used in proportion to the least common letter which is q
    letter_score_dict = {"e": 56.88, "a": 43.31, "r": 38.64, "i": 38.45, "o": 36.51, "t": 35.43,
                         "n": 33.92, "s": 29.23, "l": 27.98, "c": 23.13, "u": 18.51, "d": 17.25,
                         "p": 16.14, "m": 15.36, "h": 15.31, "g": 12.59, "b": 10.56, "f": 9.24,
                         "y": 9.06, "w": 6.57, "k": 5.61, "v": 5.13, "x": 1.48, "z": 1.39, "j": 1.0, "q": 1.0}
    score = letter_score_dict.get(letter)
    return score


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class WordleSuggestion(Action):

    def name(self) -> Text:
        return "action_wordle_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        result = tracker.latest_message.get('text')
        previous_word = tracker.get_slot('previous_word')
        available_words = tracker.get_slot('available_words')
        available_letters = tracker.get_slot('available_letters')
        unavailable_letters = tracker.get_slot('unavailable_letters')
        slot_1 = tracker.get_slot('slot_1')
        slot_2 = tracker.get_slot('slot_2')
        slot_3 = tracker.get_slot('slot_3')
        slot_4 = tracker.get_slot('slot_4')
        slot_5 = tracker.get_slot('slot_5')
        green_letters = tracker.get_slot('green_letters')
        yellow_letters = tracker.get_slot('yellow_letters')
        yl_1 = tracker.get_slot('yl_1')
        yl_2 = tracker.get_slot('yl_2')
        yl_3 = tracker.get_slot('yl_3')
        yl_4 = tracker.get_slot('yl_4')
        yl_5 = tracker.get_slot('yl_5')

        if len(available_words) == 0:
            words = load_words_pkl()
        else:
            words = available_words

        # fills the slots and yellow letters
        i = 0
        for spot in result:
            if spot == "g":
                green_letters.append(previous_word[i])
                if i == 0:
                    slot_1 = previous_word[i]
                elif i == 1:
                    slot_2 = previous_word[i]
                elif i == 2:
                    slot_3 = previous_word[i]
                elif i == 3:
                    slot_4 = previous_word[i]
                elif i == 4:
                    slot_5 = previous_word[i]
            if spot == "y":
                if previous_word[i] in yellow_letters:
                    k = 0
                    for w in yellow_letters:
                        if w == previous_word[i]:
                            m = k
                        k += 1
                    if m == 0:
                        if k not in yl_1:
                            yl_1.remove(i)
                    elif m == 1:
                        if k not in yl_2:
                            yl_2.remove(i)
                    elif m == 2:
                        if k not in yl_3:
                            yl_3.remove(i)
                    elif m == 3:
                        if k not in yl_4:
                            yl_4.remove(i)
                    elif m == 4:
                        if k not in yl_5:
                            yl_5.remove(i)
                else:
                    yellow_letters.append(previous_word[i])
                    length = len(yellow_letters)
                    if length == 1:
                        yl_1.remove(i)
                    elif length == 2:
                        yl_2.remove(i)
                    elif length == 3:
                        yl_3.remove(i)
                    elif length == 4:
                        yl_4.remove(i)
                    elif length == 5:
                        yl_5.remove(i)

            if spot == "*":
                if previous_word[i] not in yellow_letters:
                    if previous_word[i] in available_letters:
                        available_letters.remove(previous_word[i])
                        unavailable_letters.append(previous_word[i])
            i += 1

        # takes out all the words that can't work with known information
        def check_words(word):
            for letter1 in unavailable_letters:
                if letter1 in word:
                    if letter1 not in green_letters:
                        return False
            k = 0
            for letter2 in word:
                if letter2 in green_letters:
                    if k == 0 and slot_1 != letter2:
                        return False
                    elif k == 1 and slot_2 != letter2:
                        return False
                    elif k == 2 and slot_3 != letter2:
                        return False
                    elif k == 3 and slot_4 != letter2:
                        return False
                    elif k == 4 and slot_5 != letter2:
                        return False

                if letter2 in yellow_letters:
                    y = [x for x, l in enumerate(yellow_letters) if l == letter2]
                    loc = y[0]
                    if loc == 0 and k not in yl_1:
                        return False
                    elif loc == 1 and k not in yl_2:
                        return False
                    elif loc == 2 and k not in yl_3:
                        return False
                    elif loc == 3 and k not in yl_4:
                        return False
                    elif loc == 4 and k not in yl_5:
                        return False

                k += 1

            for yl in yellow_letters:
                if yl not in word:
                    return False

            return True

        possible_words = list(filter(check_words, words))
        print(possible_words)
        # gets the words that use the most different letters
        most_different_letters = 0
        great_words = []
        for word in possible_words:
            occurrences = 0
            for letter in word:
                occurrences += word.count(letter)
            if occurrences == 5:
                great_words.append(word)
                most_different_letters = 5
            else:
                diff = occurrences - 5
                different_letters = 5 - diff
                if different_letters > most_different_letters:
                    great_words = [word]
                    most_different_letters = different_letters
                elif different_letters == most_different_letters:
                    great_words.append(word)

        if len(great_words) == 1:
            best_word = great_words[0]
        else:
            # gets the words with best score
            best_score = 0
            best_words = []
            for word in great_words:
                word_score = 0
                for letter in word:
                    word_score += letter_score(letter)
                if word_score >= best_score:
                    best_score = word_score
                    best_words = [word]
                elif word_score == best_score:
                    best_words.append(word)

            best_word = best_words[0]

        dispatcher.utter_message("The next word you should try is %s" % best_word)

        return [SlotSet("previous_word", best_word), SlotSet("available_words", possible_words),
                SlotSet("available_letters", available_letters), SlotSet("unavailable_letters", unavailable_letters),
                SlotSet("slot_1", slot_1), SlotSet("slot_2", slot_2), SlotSet("slot_3", slot_3),
                SlotSet("slot_4", slot_4), SlotSet("slot_5", slot_5), SlotSet("green_letters", green_letters),
                SlotSet("yellow_letters", yellow_letters),SlotSet("yl_1", yl_1), SlotSet("yl_2", yl_2),
                SlotSet("yl_3", yl_3), SlotSet("yl_4", yl_4),SlotSet("yl_5", yl_5)]


class ActionWeWon(Action):

    def name(self) -> Text:
        return "action_we_won"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="yay! good job, come back tomorrow")

        return [AllSlotsReset()]


class ActionWeLost(Action):

    def name(self) -> Text:
        return "action_we_lost"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="darn it, better luck tomorrow")

        return [AllSlotsReset()]
