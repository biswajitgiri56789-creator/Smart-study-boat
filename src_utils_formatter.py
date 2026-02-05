from datetime import datetime

def format_post_content(questions_by_class):
    post = "📚 *Smart Study Notes* 📚\n"
    post += "========================\n\n"
    
    for class_name, subjects in questions_by_class.items():
        post += f"🎓 *{class_name.upper()}*\n"
        post += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        for subject_name, questions in subjects.items():
            if questions:
                post += f"📖 *{subject_name}:*\n"
                
                for idx, q in enumerate(questions, 1):
                    post += f"   {idx}. {q.get('question', '')}\n"
                    
                    if q.get('chapter'):
                        post += f"      📚 অধ্যায়: {q['chapter']}\n"
                    if q.get('marks'):
                        post += f"      📝 নম্বর: {q['marks']}\n"
                    if q.get('importance') == 'very_high':
                        post += "      🔥 *১০০% পরীক্ষায় আসবে*\n"
                
                post += "\n"
    
    post += f"\n⏰ *পোস্টের সময়:* {datetime.now().strftime('%d %B, %Y %I:%M %p')}\n"
    
    return post