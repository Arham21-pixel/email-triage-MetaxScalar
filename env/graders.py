from env.models import Priority, Category, TriageResult, Label

def triage_grader(prediction: TriageResult, ground_truth: Label) -> float:
    """
    Grades the LLM predicted triage against ground truth.
    0.3 for correct priority
    0.3 for correct category
    0.4 for a professional reply string (non-empty & length > 10 chars)
    """
    score = 0.0
    
    if prediction.priority == ground_truth.priority:
        score += 0.3
        
    if prediction.category == ground_truth.category:
        score += 0.3
        
    if prediction.reply and len(prediction.reply.strip()) > 10:
        score += 0.4
        
    return score
