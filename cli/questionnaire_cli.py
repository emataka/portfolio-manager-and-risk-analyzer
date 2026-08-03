from core.profiling.questionnaire import QUESTIONS
from core.profiling.risk_profiler import RiskProfiler


def ask_question(question):
    print(question["text"])
    for i, option in enumerate(question["options"], start=1):
        print(f"{i}. {option['text']}")
    choice = int(input("انتخاب شما: "))
    return question["options"][choice - 1]["score"]

def run_questionnaire():
    answers = []
    
    for question in QUESTIONS:
        score = ask_question(question)
        answers.append(score)
    
    profiler = RiskProfiler()
    return profiler.calculate_profile(answers)
