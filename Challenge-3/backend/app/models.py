import random

def rag_lawyer(case, round_num=0):
    responses = [
        f"As prosecution, precedent supports liability in {case}.",
        f"Counterpoint: The defense overlooks statutory duties relevant to {case}.",
        f"Final note: Courts usually side with established precedent in {case}."
    ]
    return responses[round_num % len(responses)]

def chaos_lawyer(case, round_num=0):
    responses = [
        f"As defense, I argue wildly: What if {case} was staged?",
        f"Counterattack: Suppose aliens influenced {case}!",
        f"Closing chaos: If a toaster can talk, why not in {case}?"
    ]
    return responses[round_num % len(responses)]

def judge(case, rag_turns, chaos_turns):
    # Very naive rule: pick RAG if more structured, Chaos if funnier
    if random.random() > 0.5:
        return "⚖️ Judge: I rule in favor of RAG Lawyer — stronger precedent."
    else:
        return "⚖️ Judge: I side with Chaos Lawyer — creativity prevails."
