def validate_post_content(content: str) -> bool:
    if not content or len(content.strip()) == 0:
        return False
    
    if len(content) < 100:
        return False
    
    required_keywords = ['📚', '🎓', '📖']
    for keyword in required_keywords:
        if keyword not in content:
            return False
    
    return True

def validate_question(question):
    errors = []
    
    required_fields = ['class', 'subject', 'question']
    
    for field in required_fields:
        if field not in question or not question[field]:
            errors.append(f"Missing required field: {field}")
    
    if 'question' in question and len(question['question']) > 500:
        errors.append("Question too long")
    
    return errors