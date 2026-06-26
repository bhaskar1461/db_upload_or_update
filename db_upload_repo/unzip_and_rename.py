"""
Unzip NCERT textbook ZIPs and rename chapter PDFs to match the notes structure.
Creates the same folder hierarchy as the notes directory.

NCERT ZIP naming convention:
  k = Class 11, l = Class 12
  h = Hindi medium, e = English medium
  Next 2 letters = subject code (ph=Physics, ch=Chemistry, bo=Biology, mh=Maths, 
    ec=Economics, ac=Accountancy, bs=Business Studies, hs=History, gy=Geography,
    ps=Political Science, sy=Sociology, st=Statistics, pe=Phys Ed,
    hb/sp/ww=English textbooks, at/vt=Hindi textbooks)
  Then part number (1,2,3)
  Inside ZIP: code + chapter number (01,02...) + .pdf
  Special suffixes: ps=prelim, an=answer, a1/a2=appendix, gl=glossary, sm=summary
"""

import zipfile
import os
import shutil

ZIP_DIR = r"c:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\class 11 and 12 text book"
OUT_DIR = r"c:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\class 11 and 12 text book"

# ============================================================
# CLASS 11 SCIENCE
# ============================================================

class11_physics = {
    "zip_codes": ["khph1", "khph2"],
    "path": "Class 11th Science/भौतिकी (Physics)",
    "chapters": {
        "khph101": "1. मात्रक और मापन",
        "khph102": "2. सरल रेखा में गति",
        "khph103": "3. समतल में गति",
        "khph104": "4. गति के नियम",
        "khph105": "5. कार्य, ऊर्जा और शक्ति",
        "khph106": "6. कणों के निकाय तथा घूर्णी गति",
        "khph107": "7. गुरुत्वाकर्षण",
        "khph201": "8. ठोसों के यांत्रिक गुण",
        "khph202": "9. तरल, द्रव के यांत्रिक गुण",
        "khph203": "10. द्रव्य के तापीय गुण",
        "khph204": "11. ऊष्मागतिकी",
        "khph205": "12. अणुगति सिद्धांत",
        "khph206": "13. दोलन गति",
        "khph207": "14. तरंगे",
    }
}

class11_chemistry = {
    "zip_codes": ["khch1", "khch2"],
    "path": "Class 11th Science/रसायन विज्ञान (Chemistry)",
    "chapters": {
        "khch101": "1. रसायन विज्ञान की कुछ मूल अवधरणाएँ",
        "khch102": "2. परमाणु की संरचना",
        "khch103": "3. तत्त्वों का वर्गीकरण एवं गुणधर्मों में आवर्तिता",
        "khch104": "4. रासायनिक आबंधन तथा आण्विक संरचना",
        "khch105": "5. ऊष्मागतिकी",
        "khch106": "6. साम्यावस्था",
        "khch201": "7. अपचयोपचय अभिक्रियाएं",
        "khch202": "8. कार्बनिक रसायन_ कुछ आधारभूत सिद्धांत तथा तकनीकें",
        "khch203": "9. हाइड्रोकार्बन",
    }
}

class11_biology = {
    "zip_codes": ["khbo1"],
    "path": "Class 11th Science/जीव विज्ञान (Biology)",
    "chapters": {
        "khbo101": "1. जीव जगत",
        "khbo102": "2. जीव जगत का वर्गीकरण",
        "khbo103": "3. वनस्पति जगत",
        "khbo104": "4. प्राणि जगत",
        "khbo105": "5. पुष्पी पादपों की आकारिकी",
        "khbo106": "6. पुष्पी पादपों का शरीर",
        "khbo107": "7. प्राणियों में संरचनात्मक संगठन",
        "khbo108": "8. कोशिका जीवन की इकाई",
        "khbo109": "9. जैव अणु",
        "khbo110": "10. कोशिका चक्र और कोशिका विभाजन",
        "khbo111": "11. उच्च पादपों में प्रकाश-संश्लेषण",
        "khbo112": "12. पादप में श्वसन",
        "khbo113": "13. पादप वृद्धि एवं परिवर्धन",
        "khbo114": "14. श्वसन और गैसों का विनिमय",
        "khbo115": "15. शरीर द्रव तथा परिसंचरण",
        "khbo116": "16. उत्सर्जी उत्पाद एवं उनका निष्कासन",
        "khbo117": "17. गमन एवं संचलन",
        "khbo118": "18. तंत्रिकीय नियंत्रण एवं समन्वय",
        "khbo119": "19. रासायनिक समन्वय तथा एकीकरण",
    }
}

class11_maths = {
    "zip_codes": ["khmh1"],
    "path": "Class 11th Science/गणित (Maths)",
    "chapters": {
        "khmh101": "1. समुच्चय",
        "khmh102": "2. संबंध और फलन",
        "khmh103": "3. त्रिकोणमीतीय फलन",
        "khmh104": "4. सम्मिश्र संख्याएँ और द्विघातीय समीकरण",
        "khmh105": "5. रैखिक असामिकाएँ",
        "khmh106": "6. क्रमचय और संचयं",
        "khmh107": "7. द्विपद प्रमेय",
        "khmh108": "8.अनुक्रम तथा श्रेणी",
        "khmh109": "9. सरल रेखाएँ",
        "khmh110": "10. शंकु परिच्छेद",
        "khmh111": "11. त्रिविमीय ज्यामिति का परिचय",
        "khmh112": "12.सीमा और अवकलज",
        "khmh113": "13. सांख्यिकी",
        "khmh114": "14. प्रायिकता",
    }
}

# ============================================================
# CLASS 11 COMMERCE
# ============================================================

class11_economics_micro = {
    "zip_codes": ["khec1"],
    "path": "Class 11th Commerce/अर्थशास्त्र (Economics)/व्यष्टि अर्थशास्त्र (Micro Economics)",
    "chapters": {
        "khec101": "1. परिचय",
        "khec102": "2. उपभोक्ता के व्यवहार का सिद्धान्त",
        "khec103": "3. उत्पादन तथा लागत",
        "khec104": "4. पूर्ण प्रतिस्पर्धा की स्थिति में फर्म का सिद्धान्त",
        "khec105": "5. बाज़ार संतुलन",
    }
}

class11_economics_stats = {
    "zip_codes": ["khst1"],
    "path": "Class 11th Commerce/अर्थशास्त्र (Economics)/सांख्यिकी (Statistics)",
    "chapters": {
        "khst101": "1. परिचय",
        "khst102": "2. आँकड़ों का संग्रह",
        "khst103": "3. आँकड़ों का संगठन",
        "khst104": "4. आँकड़ों का प्रस्तुतीकरण",
        "khst105": "5. केन्द्रीय प्रवृति के माप",
        "khst106": "6. सहसंबंध",
        "khst107": "7. सूचकांक",
    }
}

class11_accountancy = {
    "zip_codes": ["khac1", "khac2"],
    "path": "Class 11th Commerce/लेखाशास्त्र (Accountancy)",
    "chapters": {
        "khac101": "1. लेखांकन-एक परिचय",
        "khac102": "2. लेखांकन के सैद्धांतिक आधार",
        "khac103": "3. लेन-देनों का अभिलेखन-1",
        "khac104": "4. लेन-देनों का अभिलेखन-2",
        "khac105": "5. बैंक समाधान विवरण",
        "khac106": "6. तलपट एवं अशुद्धियों का शोधन",
        "khac107": "7. ह्रास_ प्रावधान और संचय",
        "khac201": "8. वित्तीय विवरण-I",
        "khac202": "9. वित्तीय विवरण-II",
    }
}

class11_business = {
    "zip_codes": ["khbs1"],
    "path": "Class 11th Commerce/व्यवसाय अध्ययन (Business Studies)",
    "chapters": {
        "khbs101": "1. व्यवसाय, व्यापार और वाणिज्य",
        "khbs102": "2. व्यावसायिक संगठन के स्वरुप",
        "khbs103": "3. निजी, सार्वजनिक एवं भूमंडलीय उपक्रम",
        "khbs104": "4. व्यावसायिक सेवाएँ",
        "khbs105": "5. व्यवसाय की उभरती पद्धतियाँ",
        "khbs106": "6. व्यवसाय का सामाजिक उत्तरदायित्व एवं व्यावसायिक नैतिकता",
        "khbs107": "7. कंपनी निर्माण",
        "khbs108": "8. व्यवसायिक वित् के स्रोत",
        "khbs109": "9. लघु व्यवसाय",
        "khbs110": "10. आंतरिक व्यापार",
        "khbs111": "11. अंतर्राष्ट्रीय व्यापार",
    }
}

# ============================================================
# CLASS 11 HUMANITIES
# ============================================================

class11_history = {
    "zip_codes": ["khhs1"],
    "path": "Class 11th Humanities/इतिहास  (History)",
    "chapters": {
        "khhs101": "1. लेखन कला और शहरी जीवन",
        "khhs102": "2. तीन महाद्वीपों में फैला हुआ साम्राज्य",
        "khhs103": "3. यायावर साम्राज्य",
        "khhs104": "4. तीन वर्ग",
        "khhs105": "5. बदलती हुई सांस्कृतिक परम्पराएँ",
        "khhs106": "6. मूल निवासियों का विस्थापन",
        "khhs107": "7. आधुनिकीकरण के रास्ते",
    }
}

class11_geography = {
    "zip_codes": ["khgy1", "khgy2", "khgy3"],
    "path": "Class 11th Humanities/भूगोल (Geography)/खण्ड - 1  भौतिक भूगोल के मूल सिद्धांत",
    "chapters": {
        # Only the chapters that exist in notes
        "khgy105": "5 भू – आकृतिक प्रक्रियाएँ",
        "khgy208": "8 सौर विकिरण , ऊष्मा संतुलन एवं तापमान",
        "khgy212": "12 महासागरीय जल",
        "khgy214": "14 जैव विविधता एवं संरक्षण",
    }
}

class11_polsci_constitution = {
    "zip_codes": ["khps1"],
    "path": "Class 11th Humanities/राजनीति विज्ञान (Political Science)/भारत का संविधान सिद्धांत और व्यवहार",
    "chapters": {
        "khps101": "1 संविधान - क्यों और कैसे",
        "khps102": "2 भारतीय संविधान में अधिकार",
        "khps103": "3 चुनाव और प्रतिनिधित्व",
        "khps104": "4. कार्यपालिका",
        "khps105": "5. विधायिका",
        "khps106": "6. न्यायपालिका",
        "khps107": "7. संघवाद",
        "khps108": "8. स्थानीय शासन",
    }
}

class11_polsci_theory = {
    "zip_codes": ["khps2"],
    "path": "Class 11th Humanities/राजनीति विज्ञान (Political Science)/राजनीतिक सिद्धांत",
    "chapters": {
        "khps201": "1. राजनीतिक सिद्धांत-एक परिचय",
        "khps202": "2. स्वतंत्रता",
        "khps203": "3. समानता",
        "khps204": "4. सामाजिक न्याय",
        "khps205": "5. अधिकार",
        "khps206": "6. नागरिकता",
        "khps207": "7. राष्ट्रवाद",
        "khps208": "8. धर्मनिरपेक्षता",
    }
}

class11_sociology = {
    "zip_codes": ["khsy1", "khsy2"],
    "path": "Class 11th Humanities/समाजशास्त्र (Sociology)",
    "chapters": {
        "khsy101": "1. समाजशास्त्र एवं समाज",
        "khsy102": "2. समाजशास्त्र में प्रयुक्त शब्दावली संकल्पनाएँ एवं उनका उपयोग",
        "khsy103": "3. सामाजिक संस्थाओं को समझना",
        "khsy104": "4. संस्कृति तथा समाजीकरण",
        "khsy105": "5. समाजशास्त्र अनुसंधान पद्धतियाँ",
        "khsy201": "6. समाज में सामाजिक संरचना , स्तरीकरण और सामाजिक प्रक्रियाएँ",
        "khsy202": "7. ग्रामीण तथा नगरीय समाज में सामाजिक परिवर्तन एवं सामाजिक व्यवस्था",
        "khsy203": "8. पर्यावरण और समाज",
        "khsy204": "9. पाश्चात्य समाजशास्त्री एक परिचय",
        "khsy205": "10. भारतीय समाजशास्त्री",
    }
}

class11_pe = {
    "zip_codes": [],  # No specific PE textbook from NCERT in our downloads
    "path": "Class 11th Science/शारीरिक शिक्षा (Physical Education)",
    "chapters": {}
}

# ============================================================
# CLASS 12 SCIENCE
# ============================================================

class12_physics = {
    "zip_codes": ["lhph1", "lhph2"],
    "path": "Class 12th Science/भौतिकी (Physics)",
    "chapters": {
        "lhph101": "1. वैद्युत आवेश",
        "lhph102": "2. स्थिर वैद्युत विभव तथा धारिता",
        "lhph103": "3. विद्युत धारा",
        "lhph104": "4. गतिमान आवेश और चुंबकत्व",
        "lhph105": "5. चुंबकत्व एवं द्रव्य",
        "lhph106": "6. विद्युत चुम्बकीय प्रेरण",
        "lhph107": "7. प्रत्यावर्ती धारा",
        "lhph108": "8. विद्युत चुंबकीय तरंगें",
        "lhph201": "9. किरण प्रकाशिकी एवं प्रकाशिक यंत्र",
        "lhph202": "10. तरंग प्रकाशिकी",
        "lhph203": "11. विकिरण तथा द्रव्य की द्वेती प्रकृति",
        "lhph204": "12. परमाणु",
        "lhph205": "13. नाभिक",
        "lhph206": "14. अर्धचालक",
    }
}

class12_chemistry = {
    "zip_codes": ["lhch1", "lhch2"],
    "path": "Class 12th Science/रसायन विज्ञान (Chemistry)",
    "chapters": {
        "lhch101": "1. विलयन",
        "lhch102": "2. वैद्युतरसायन",
        "lhch103": "3. रासायनिक बलगतिकी",
        "lhch104": "4. d-एवं f-ब्लॉक के तत्व",
        "lhch105": "5. उपसहसंयोजन यौगिक",
        "lhch201": "7. एल्कोहल, फिनॉल एवं ईथर",
        "lhch202": "8. एल्डिहाइड, कीटोन एवं कार्बोक्सिलिक अम्ल",
        "lhch203": "9. ऐमीन",
        "lhch204": "10. जैव-अणु",
    }
}

class12_biology = {
    "zip_codes": ["lhbo1"],
    "path": "Class 12th Science/जीव विज्ञान (Biology)",
    "chapters": {
        "lhbo101": "1. पुष्पी पादपों में लैंगिक प्रजनन",
        "lhbo102": "2. मानव जनन",
        "lhbo103": "3. जनन स्वास्थ्य",
        "lhbo104": "4. वंशागति तथा विविधता के सिद्धांत",
        "lhbo105": "5. वंशागति का आणविक आधार",
        "lhbo106": "6. विकास",
        "lhbo107": "7. मानव स्वास्थ्य तथा रोग",
        "lhbo108": "8. मानव कल्याण में सूक्ष्म जीव",
        "lhbo109": "9. जैव प्रौद्योगिकी-सिद्धांत व प्रक्रम",
        "lhbo110": "10. जैव प्रौद्योगिकी एवं उसके उपयोग",
        "lhbo111": "11. जीव और समष्टियाँ",
        "lhbo112": "12. पारितंत्र",
        "lhbo113": "13. जीव विविधतता एवं संरक्षण",
    }
}

class12_maths = {
    "zip_codes": ["lhmh1", "lhmh2"],
    "path": "Class 12th Science/गणित (Maths)",
    "chapters": {
        "lhmh101": "1. संबंध एवं फलन",
        "lhmh102": "2. प्रतिलोम त्रिकोणमितीय फलन",
        "lhmh103": "3. आव्यूह",
        "lhmh104": "4. सारणिक",
        "lhmh105": "5. सांतत्य तथा अवकलनीयता",
        "lhmh106": "6. अवकलज के अनुप्रयोग",
        "lhmh201": "7. समाकलन",
        "lhmh202": "8. समाकलनों के अनुप्रयोग",
        "lhmh203": "9. अवकल समीकरण",
        "lhmh204": "10. सदिश बीजगणित",
        "lhmh205": "11. त्रि-विमीय ज्यामिती",
        "lhmh206": "12. रैखिक प्रोग्रामन",
        "lhmh207": "13. प्रायिकता",
    }
}

class12_pe = {
    "zip_codes": [],
    "path": "Class 12th Science/शारीरिक शिक्षा (Physical Education)",
    "chapters": {}
}

# ============================================================
# CLASS 12 COMMERCE
# ============================================================

class12_economics_macro = {
    "zip_codes": ["lhec1"],
    "path": "Class 12th Commerce/अर्थशास्त्र (Economics)/समष्टि अर्थशास्त्र (Macro Economics)",
    "chapters": {
        "lhec101": "1. परिचय",
        "lhec102": "2. राष्ट्रीय आय का लेखांकन",
        "lhec103": "3. मुद्रा और बैंकिंग",
        "lhec104": "4. आय और रोजगार के निर्धारण",
        "lhec105": "5. सरकारी बजट एवं अर्थव्यवस्था",
        "lhec106": "6. खुली अर्थव्यवस्थाः समष्टि अर्थशास्त्र",
    }
}

class12_economics_indian = {
    "zip_codes": ["lhec2"],
    "path": "Class 12th Commerce/अर्थशास्त्र (Economics)/भारतीय अर्थव्यवस्था का विकास (Indian Economy Development)",
    "chapters": {
        "lhec201": "1 स्वतंत्रता की पूर्व संध्या पर भारतीय अर्थव्यवस्था",
        "lhec202": "2 भारतीय अर्थव्यवस्था 1950 - 1990",
        "lhec203": "3 उदारीकरण_ निजीकरण और वैश्वीकरणः एक समीक्षा",
        "lhec204": "4 भारत में मानव पूँजी निर्माण",
        "lhec205": "5 ग्रामीण विकास",
    }
}

class12_accountancy = {
    "zip_codes": ["lhac1", "lhac2"],
    "path": "Class 12th Commerce/लेखाशास्त्र (Accountancy)",
    "chapters": {
        "lhac101": "1. साझेदारी लेखांकन - आधारभूत अवधारणाएँ",
        "lhac102": "2. साझेदारी फर्म का पुनर्गठन. साझेदार का प्रवेश",
        "lhac103": "3. साझेदारी फर्म का पुनर्गठन - साझेदार की सेवानिवृत्ति-मृत्यु",
        "lhac104": "4. साझेदारी फर्म का विघटन",
        "lhac201": "5. अंश पूँजी के लिए लेखांकन",
        "lhac202": "6. ऋणपत्रो का नियम एवम मोचन",
        "lhac203": "7. कम्पनी के वित्तीय विवरण",
        "lhac204": "8. लेखांकन अनुपात",
        "lhac205": "9. रोकड़ प्रवाह विवरण",
    }
}

class12_business = {
    "zip_codes": ["lhbs1", "lhbs2"],
    "path": "Class 12th Commerce/व्यवसाय अध्ययन (Business Studies)",
    "chapters": {
        "lhbs101": "1. प्रबंध की प्रकृति एवं महत्त्व",
        "lhbs102": "2. प्रबंध के सिद्धांत",
        "lhbs103": "3. व्यावसायिक वातवरण",
        "lhbs104": "4. नियोजन",
        "lhbs105": "5.संगठन",
        "lhbs106": "6. नियुक्तिकरण",
        "lhbs107": "7. निर्देशन",
        "lhbs108": "8. नियंत्रण",
        "lhbs201": "9. व्यावसायिक वित्त",
        "lhbs202": "10. विपणन",
        "lhbs203": "11. उपभोक्ता संरक्षण",
    }
}

# ============================================================
# CLASS 12 HUMANITIES
# ============================================================

class12_history_1 = {
    "zip_codes": ["lhhs1"],
    "path": "Class 12th Humanities/इतिहास (History)/भारतीय इतिहास के कुछ विषय-I",
    "chapters": {
        "lhhs101": "1. ईंटें_ मनके तथा अस्थियाँ हड़प्पा सभ्यता",
        "lhhs102": "2. राजा_ किसान और नगर आरंभिक राज्य और अर्थव्यवस्थाएँ",
        "lhhs103": "3. बंधुत्व जाति तथा वर्ग आरंभिक समाज (600 ईपू से 600 ईसवी)",
        "lhhs104": "4. विचारक, विश्वास और इमारतें",
    }
}

class12_history_2 = {
    "zip_codes": ["lhhs2"],
    "path": "Class 12th Humanities/इतिहास (History)/भारतीय इतिहास  के कुछ विषय-II",
    "chapters": {
        "lhhs201": "1. यात्रियों के नजरिए",
        "lhhs202": "2. भक्ति – सूफी पंरपराएँ",
        "lhhs203": "3. एक साम्राज्य की राजधानी विजयनगर",
        "lhhs204": "4. किसान जमींदार और राज्य",
    }
}

class12_history_3 = {
    "zip_codes": ["lhhs3"],
    "path": "Class 12th Humanities/इतिहास (History)/भारतीय इतिहास के कुछ विषय-III",
    "chapters": {
        "lhhs301": "1. उपनिवेशवाद और देहात",
        "lhhs302": "2. विद्रोही और राज",
        "lhhs303": "3. महात्मा गाँधी और राष्ट्रीय आंदोलन",
        "lhhs304": "4. संविधान का निर्माण",
    }
}

class12_geography_1 = {
    "zip_codes": ["lhgy1"],
    "path": "Class 12th Humanities/भूगोल (Geography)/भाग  1 मानव भूगोल के मूल सिद्धान्त",
    "chapters": {
        "lhgy101": "1. मानव भूगोल प्रकृति एवं विषय क्षेत्र",
        "lhgy102": "2. विश्व जनसंख्या वितरण , घनत्व और वृद्धि",
        "lhgy103": "3. मानव विकास",
        "lhgy104": "4. प्राथमिक क्रियाएँ",
        "lhgy105": "5. द्वितीयक क्रियाएँ",
        "lhgy106": "6. तृतीयक और चतुर्थ क्रियाकलाप",
        "lhgy107": "7. परिवहन एवं संचार",
        "lhgy108": "8. अंतर्राष्ट्रीय व्यापार",
    }
}

class12_geography_2 = {
    "zip_codes": ["lhgy2"],
    "path": "Class 12th Humanities/भूगोल (Geography)/भाग  2 भारत  लोग एवं अर्थव्यवस्था",
    "chapters": {
        "lhgy201": "1. जनसंख्या वितरण , घनत्व , वृद्धि और संघटन",
        "lhgy202": "2. मानव बस्तियाँ",
        "lhgy203": "3. जल संसाधन",
        "lhgy204": "4. खनिज तथा ऊर्जा संसाधन",
        "lhgy205": "5. भारत के संदर्भ में नियोजन एवं सततपोषणीय विकास",
        "lhgy206": "6. परिवहन तथा संचार",
        "lhgy207": "7. अन्तर्राष्ट्रीय व्यापार",
        "lhgy208": "8.भौगोलिक परिपेक्ष्य मेंचयनित क ु छ म ुद्दे एवं समस्याएँ",
    }
}

class12_sociology_1 = {
    "zip_codes": ["lhsy1"],
    "path": "Class 12th Humanities/समाजशास्त्र (Sociology)/नागरिक सास्त्र भारतीय समाज",
    "chapters": {
        "lhsy101": "1. भारतीय समाज एक परिचय",
        "lhsy102": "2. भारतीय समाज की जनसांख्यिकीय संरचना",
        "lhsy103": "3. सामाजिक संस्थाएँ निरंतरता एवं परिवर्तन",
        "lhsy104": "4. बाज़ार एक सामाजिक संस्था के रूप में",
        "lhsy105": "5. सामाजिक विषमता एवं बहिष्कार के स्वरूप",
        "lhsy106": "6. सांस्कृतिक विविधता की चुनौतियाँ",
        "lhsy107": "7. परियोजना कार्य के लिए सुझाव",
    }
}

class12_sociology_2 = {
    "zip_codes": ["lhsy2"],
    "path": "Class 12th Humanities/समाजशास्त्र (Sociology)/नागरिक सास्त्र भारत में सामाजिक परिवर्तन और विकास",
    "chapters": {
        "lhsy201": "1. संरचनात्मक परिवर्तन",
        "lhsy202": "2. सांस्कृतिक परिवर्तन",
        "lhsy203": "3. ग्रामीण समाज में विकास एवं परिवर्तन",
        "lhsy204": "4. औद्योगिक समाज में परिवर्तन और विकास",
        "lhsy205": "5. भूमंडलीकरण और सामाजिक परिवर्तन",
        "lhsy206": "6. जनसंपर्क साधन और जनसंचार",
        "lhsy207": "7. सामाजिक आंदोलन",
    }
}

class12_polsci_1 = {
    "zip_codes": ["lhps1"],
    "path": "Class 12th Humanities/राजनीति विज्ञान (Political Science - if exists)",
    "chapters": {}  # No pol sci notes found for class 12
}

# ============================================================
# ALL SUBJECTS
# ============================================================

ALL_SUBJECTS = [
    class11_physics, class11_chemistry, class11_biology, class11_maths,
    class11_economics_micro, class11_economics_stats, class11_accountancy, class11_business,
    class11_history, class11_geography, class11_polsci_constitution, class11_polsci_theory,
    class11_sociology,
    class12_physics, class12_chemistry, class12_biology, class12_maths,
    class12_economics_macro, class12_economics_indian, class12_accountancy, class12_business,
    class12_history_1, class12_history_2, class12_history_3,
    class12_geography_1, class12_geography_2,
    class12_sociology_1, class12_sociology_2,
]


def process_subject(subject):
    chapters = subject["chapters"]
    if not chapters:
        return 0

    out_path = os.path.join(OUT_DIR, subject["path"])
    os.makedirs(out_path, exist_ok=True)

    count = 0
    # Collect all PDFs from all ZIPs for this subject
    for zip_code in subject["zip_codes"]:
        zip_path = os.path.join(ZIP_DIR, f"{zip_code}.zip")
        if not os.path.exists(zip_path):
            print(f"  WARNING: ZIP not found: {zip_path}")
            continue

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for entry in z.infolist():
                    if entry.is_dir():
                        continue
                    fname = entry.filename
                    base = os.path.splitext(fname)[0]  # e.g. "khph101"

                    if base in chapters:
                        new_name = chapters[base] + ".pdf"
                        target = os.path.join(out_path, new_name)
                        # Extract to temp then rename
                        data = z.read(entry.filename)
                        with open(target, "wb") as f:
                            f.write(data)
                        print(f"  ✓ {fname} -> {new_name}")
                        count += 1
                    else:
                        # Extract supplementary files (prelim, answers, appendix, glossary) as-is
                        target = os.path.join(out_path, fname)
                        data = z.read(entry.filename)
                        with open(target, "wb") as f:
                            f.write(data)
        except Exception as e:
            print(f"  ERROR processing {zip_code}: {e}")

    return count


total = 0
for subject in ALL_SUBJECTS:
    if subject["chapters"]:
        print(f"\n{'='*60}")
        print(f"Processing: {subject['path']}")
        print(f"{'='*60}")
        n = process_subject(subject)
        total += n
        print(f"  Renamed {n} chapter PDFs")

print(f"\n{'='*60}")
print(f"DONE! Total chapters renamed: {total}")
print(f"{'='*60}")
