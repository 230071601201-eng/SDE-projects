def calculate_priority(call):
    score = 0
    
    if call["urgency"] == "high":
        score += 50
    elif call["urgency"] == "medium":
        score += 30
    else:
        score += 10

    if call["customer_type"] == "premium":
        score += 40

    if call["waiting_time"] > 10:
        score += 20

    return score