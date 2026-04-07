from env.models import Priority, Category, TriageResult, Label

def task1_grader(prediction: TriageResult, ground_truth: Label) -> float:
    score = 0.01
    if prediction.priority == ground_truth.priority:
        score += 0.98
    return min(max(score, 0.01), 0.99)

def task2_grader(prediction: TriageResult, ground_truth: Label) -> float:
    score = 0.01
    if prediction.priority == ground_truth.priority:
        score += 0.49
    if prediction.category == ground_truth.category:
        score += 0.49
    return min(max(score, 0.01), 0.99)

def task3_grader(prediction: TriageResult, ground_truth: Label) -> float:
    score = 0.01
    if prediction.priority == ground_truth.priority:
        score += 0.3
    if prediction.category == ground_truth.category:
        score += 0.3
    if prediction.reply and len(prediction.reply.strip()) > 10:
        score += 0.38
    return min(max(score, 0.01), 0.99)

def task1(prediction: TriageResult, ground_truth: Label) -> float: return task1_grader(prediction, ground_truth)
def task2(prediction: TriageResult, ground_truth: Label) -> float: return task2_grader(prediction, ground_truth)
def task3(prediction: TriageResult, ground_truth: Label) -> float: return task3_grader(prediction, ground_truth)

def triage_grader(prediction: TriageResult, ground_truth: Label) -> float:
    """
    Grades the LLM predicted triage against ground truth.
    0.3 for correct priority
    0.3 for correct category
    0.4 for a professional reply string (non-empty & length > 10 chars)
    """
    score = task3_grader(prediction, ground_truth)
        
    return score
