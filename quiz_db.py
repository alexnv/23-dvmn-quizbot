import json
import random


def get_random_question():
    with open('quiz_bank.json', 'r', encoding='UTF-8') as file:
        quiz_bank = json.load(file)
    question, _ = random.choice(list(quiz_bank.items()))
    return question


def get_answer(question):
    with open('quiz_bank.json', 'r', encoding='UTF-8') as file:
        quiz_bank = json.load(file)
    answer = quiz_bank.get(question)
    simple_answer = answer.partition('.')[0].partition('(')[0]
    return simple_answer
