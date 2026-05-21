from apps.ai_interventions.models import MessageType

TEMPLATES = {
    MessageType.APPOINTMENT_REMINDER: {
        "en": "Hi {patient_name}, this is a gentle reminder about your upcoming visit for {treatment_name}. Reply if you need to reschedule. — {clinic_name}",
        "ta": "வணக்கம் {patient_name}, உங்கள் {treatment_name} வருகைக்கான மென்மையான நினைவூட்டல். மாற்ற வேண்டுமானால் தெரிவியுங்கள். — {clinic_name}",
        "hi": "नमस्ते {patient_name}, आपकी {treatment_name} अपॉइंटमेंट की विनम्र याद दिलाना है। बदलाव चाहिए तो बताएं। — {clinic_name}",
        "te": "హాయ్ {patient_name}, మీ {treatment_name} అపాయింట్మెంట్ కోసం చిన్న గుర్తింపు. మార్చాలంటే తెలియజేయండి. — {clinic_name}",
    },
    MessageType.MISSED_FOLLOWUP: {
        "en": "Hi {patient_name}, we missed you at your last visit. Would you like help finding a new time? We are here for you. — {clinic_name}",
        "ta": "வணக்கம் {patient_name}, உங்கள் கடந்த வருகையை தவற விட்டோம். புதிய நேரம் கண்டுபிடிக்க உதவலாமா? — {clinic_name}",
        "hi": "नमस्ते {patient_name}, आपकी पिछली विज़िट छूट गई। क्या नया समय तय करने में मदद चाहिए? — {clinic_name}",
        "te": "హాయ్ {patient_name}, మీ చివరి విజిట్ మిస్ అయ్యింది. కొత్త సమయం ఫిక్స్ చేయడంలో సహాయం కావాలా? — {clinic_name}",
    },
    MessageType.TREATMENT_ENCOURAGEMENT: {
        "en": "Hi {patient_name}, you are making progress on {treatment_name}. Staying consistent keeps results on track. We are with you. — {doctor_name}",
        "ta": "வணக்கம் {patient_name}, உங்கள் {treatment_name} முன்னேற்றம் நன்றாக உள்ளது. தொடர்ச்சியாக வருவது முக்கியம். — {doctor_name}",
        "hi": "नमस्ते {patient_name}, आपकी {treatment_name} प्रगति अच्छी है। नियमित रहना परिणामों में मदद करता है। — {doctor_name}",
        "te": "హాయ్ {patient_name}, మీ {treatment_name} మంచి పురోగతి. క్రమంగా రావడం ఫలితాలకు మంచిది. — {doctor_name}",
    },
    MessageType.MOTIVATIONAL: {
        "en": "Hi {patient_name}, small steps add up. Your oral health journey matters, and we are here to support you. — {clinic_name}",
        "ta": "வணக்கம் {patient_name}, சிறிய முன்னேற்றமும் முக்கியம். உங்கள் வாய்ச் சுகாதாரம் எங்களுக்குப் முக்கியம். — {clinic_name}",
        "hi": "नमस्ते {patient_name}, छोटे कदम भी बड़ा असर करते हैं। आपकी ओरल हेल्थ हमारे लिए महत्वपूर्ण है। — {clinic_name}",
        "te": "హాయ్ {patient_name}, చిన్న అడుగులు కూడా గొప్ప మార్పు ఇస్తాయి. మీ ఆరోగ్యం మా కోసం ముఖ్యమే. — {clinic_name}",
    },
    MessageType.EDUCATIONAL: {
        "en": "Quick tip: gentle brushing and regular check-ins protect your smile. Let us know if you have questions. — {clinic_name}",
        "ta": "சிறிய குறிப்புகள்: மென்மையான துலக்கலும் வழக்கமான சரிபார்ப்பும் புன்னகையை பாதுகாக்கும். — {clinic_name}",
        "hi": "छोटा टिप: हल्का ब्रश और नियमित चेकअप आपकी मुस्कान को सुरक्षित रखते हैं। — {clinic_name}",
        "te": "చిన్న టిప్: మృదువైన బ్రషింగ్, రెగ్యులర్ చెక్-ఇన్ మీ నవ్వును కాపాడుతుంది. — {clinic_name}",
    },
}


def render_template(message_type: str, language: str, context: dict) -> tuple[str, str]:
    templates = TEMPLATES.get(message_type) or {}
    template = templates.get(language) or templates.get("en")
    if not template:
        return "", ""

    content = template.format(**context)
    return content, f"{message_type}:{language}"
