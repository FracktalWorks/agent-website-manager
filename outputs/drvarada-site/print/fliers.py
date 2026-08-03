"""Flier copy — four conditions, three languages. Data only, no markup.

PROVENANCE MATTERS MORE THAN USUAL HERE
    A flier is a medical claim a patient takes home and shows their family. So
    every line below is either lifted from a page already published on
    drvarada.com, or written here and marked as such — see `SOURCE`. The
    difference decides which gate a flier passes.

    · vitiligo, psoriasis — Telugu and Hindi come from `/te/` and `/hi/` pages
      that have been live and in-language since launch. Not machine-translated
      from the English, and not retyped: the glance rows are the same facts in
      the same words.
    · hair-loss, acne — no in-language page exists, so the Telugu and Hindi
      here were WRITTEN FOR THIS FLIER and have never been read by a native
      speaker. They render correctly; that is not the same as reading
      correctly. `flier.py` holds them as stamped proofs.

WHAT EVERY FLIER MUST SAY
    The clinic's position is that the honest limit is part of the offer, not a
    disclaimer under it. Vitiligo and psoriasis are not curable, hair takes
    months to answer, and acne scars improve rather than vanish. Each flier
    carries that as a titled section — `truth` — set in the same size as the
    treatments, not smaller.
"""

from __future__ import annotations

# Per-language furniture. Kept beside the copy rather than in the renderer, so
# adding a fourth language is a data change and not a template change.
UI = {
    "en": {"offer": "What the clinic offers",
           "truth": "The honest part",
           "book": "Scan to book on WhatsApp",
           "more": "Full information",
           "at": "At a glance",
           "with": "With"},
    "te": {"offer": "క్లినిక్‌లో అందుబాటులో ఉన్నవి",
           "truth": "నిజం ఏమిటంటే",
           "book": "WhatsApp‌లో బుక్ చేయడానికి స్కాన్ చేయండి",
           "more": "పూర్తి సమాచారం",
           "at": "ఒక్క చూపులో",
           "with": "వైద్యులు"},
    "hi": {"offer": "क्लिनिक में उपलब्ध",
           "truth": "सच यह है",
           "book": "बुक करने के लिए स्कैन करें",
           "more": "पूरी जानकारी",
           "at": "एक नज़र में",
           "with": "चिकित्सक"},
}

LANG_NAME = {"en": "English", "te": "తెలుగు", "hi": "हिन्दी"}

# Which copy came from a published page and which was written here.
PUBLISHED = "published in-language page on drvarada.com"
WRITTEN = "written for this flier, never natively reviewed"

FLIERS = [

# ══════════════════════════════════════════════════════ vitiligo ═════════════
{
    "slug": "vitiligo", "lang": "en", "source": PUBLISHED,
    "url": "https://drvarada.com/vitiligo/",
    "eyebrow": "Vitiligo · White patches",
    "h1": "Vitiligo, explained properly.",
    "lede": "White patches are the visible part. What decides your treatment "
            "is invisible: whether the disease is still spreading, how long "
            "each patch has been there, and where on the body it sits.",
    "glance": [
        ("Also called", "Leucoderma, white patches, safed daag"),
        ("Curable", "No, but repigmentation is common"),
        ("Main treatments", "Topicals, NB-UVB, excimer, surgery"),
        ("Timeline", "Months, reviewed every 6–8 weeks"),
        ("Surgery needs", "Disease stable for 12 months"),
    ],
    "treat": [
        ("Medical treatment", "Topical and oral therapy to stop the spread"),
        ("Narrowband UVB", "Whole-body phototherapy, twice or thrice weekly"),
        ("Excimer laser", "Targeted light for a small number of patches"),
        ("Graft surgery", "For stable disease that has not repigmented"),
    ],
    "truth": "There is no cure for vitiligo anywhere in the world. What good "
             "treatment does is stop it spreading and bring colour back to "
             "patches that can respond. Anyone promising a cure is selling "
             "something.",
},
{
    "slug": "vitiligo", "lang": "te", "source": PUBLISHED,
    "url": "https://drvarada.com/te/vitiligo/",
    "eyebrow": "బొల్లి · Vitiligo",
    "h1": "బొల్లి: తెలుగులో పూర్తి సమాచారం",
    "lede": "బొల్లి అంటకుండా వచ్చే ఆటో-ఇమ్యూన్ సమస్య. ఇది అంటువ్యాధి కాదు, "
            "తిన్న ఆహారం వల్ల వచ్చేది కాదు. సరైన చికిత్సతో చాలా మందిలో మచ్చలపై "
            "రంగు తిరిగి వస్తుంది.",
    "glance": [
        ("తెలుగులో", "బొల్లి, తెల్ల మచ్చలు"),
        ("పూర్తిగా నయం", "కాదు. కానీ రంగు తిరిగి రావడం సాధ్యమే"),
        ("చికిత్సలు", "మందులు, ఫోటోథెరపీ, ఎక్సైమర్, సర్జరీ"),
        ("సమయం", "నెలలు. 6–8 వారాలకోసారి రివ్యూ"),
        ("సర్జరీకి", "12 నెలలు స్థిరంగా ఉండాలి"),
    ],
    "treat": [
        ("మందులు", "వ్యాప్తిని ఆపడానికి క్రీములు, మాత్రలు"),
        ("నారోబ్యాండ్ UVB", "శరీరమంతా ఫోటోథెరపీ, వారానికి 2–3 సార్లు"),
        ("ఎక్సైమర్ లేజర్", "కొన్ని మచ్చలకు మాత్రమే, గురిపెట్టిన కాంతి"),
        ("గ్రాఫ్ట్ సర్జరీ", "స్థిరంగా ఉండి, రంగు రాని మచ్చలకు"),
    ],
    "truth": "బొల్లిని పూర్తిగా నయం చేసే చికిత్స ప్రపంచంలో ఎక్కడా లేదు. సరైన "
             "చికిత్స చేసేది రెండే — వ్యాప్తిని ఆపడం, రంగు తిరిగి తేవడం. "
             "పూర్తిగా నయం చేస్తామని చెప్పేవాళ్లను నమ్మవద్దు.",
},
{
    "slug": "vitiligo", "lang": "hi", "source": PUBLISHED,
    "url": "https://drvarada.com/hi/vitiligo/",
    "eyebrow": "सफ़ेद दाग · Vitiligo",
    "h1": "सफ़ेद दाग: हिन्दी में पूरी जानकारी",
    "lede": "सफ़ेद दाग एक ऑटो-इम्यून स्थिति है। यह छूने से नहीं फैलता, खाने से "
            "नहीं होता, और किसी पाप की सज़ा तो बिल्कुल नहीं है। सही इलाज से "
            "ज़्यादातर मरीज़ों में रंग वापस आ सकता है।",
    "glance": [
        ("हिन्दी में", "सफ़ेद दाग, ल्यूकोडर्मा"),
        ("जड़ से इलाज", "नहीं। पर रंग वापस आना संभव"),
        ("इलाज", "दवाएँ, फोटोथेरेपी, एक्साइमर, सर्जरी"),
        ("समय", "महीनों में। हर 6–8 हफ्ते समीक्षा"),
        ("सर्जरी के लिए", "12 महीने स्थिर होना ज़रूरी"),
    ],
    "treat": [
        ("दवाएँ", "फैलाव रोकने के लिए क्रीम और गोलियाँ"),
        ("नैरोबैंड UVB", "पूरे शरीर की फोटोथेरेपी, हफ्ते में 2–3 बार"),
        ("एक्साइमर लेज़र", "गिने-चुने दागों पर लक्षित प्रकाश"),
        ("ग्राफ्ट सर्जरी", "स्थिर दाग जिन पर रंग नहीं लौटा"),
    ],
    "truth": "सफ़ेद दाग को जड़ से मिटाने वाला इलाज दुनिया में कहीं नहीं है। "
             "सही इलाज दो काम करता है — फैलाव रोकना, और रंग वापस लाना। जो "
             "जड़ से इलाज का दावा करे, वह कुछ बेच रहा है।",
},

# ═════════════════════════════════════════════════════ psoriasis ═════════════
{
    "slug": "psoriasis", "lang": "en", "source": PUBLISHED,
    "url": "https://drvarada.com/psoriasis/",
    "eyebrow": "Psoriasis",
    "h1": "Psoriasis, and how it is actually controlled.",
    "lede": "Psoriasis is not a skin infection, not contagious, and not "
            "curable. It is an immune condition that flares and settles, and "
            "good treatment lengthens the gap between flares.",
    "glance": [
        ("What it is", "An immune-driven inflammatory skin disease"),
        ("Curable", "No, but often well controlled"),
        ("Course", "Flares and remissions over years"),
        ("Main treatments", "Topicals, phototherapy, systemics, biologics"),
        ("Watch for", "Joint pain: psoriatic arthritis"),
    ],
    "treat": [
        ("Topical therapy", "The foundation, for limited disease"),
        ("Phototherapy", "Narrowband UVB for widespread plaques"),
        ("Systemic medicines", "When large areas or joints are involved"),
        ("Biologics", "For severe disease that has not responded"),
    ],
    "truth": "Psoriasis cannot be cured. It can be controlled, often for "
             "years at a time. Judge treatment by how long your skin stays "
             "settled, not by one photograph of clear skin.",
},
{
    "slug": "psoriasis", "lang": "te", "source": PUBLISHED,
    "url": "https://drvarada.com/te/psoriasis/",
    "eyebrow": "సోరియాసిస్ · Psoriasis",
    "h1": "సోరియాసిస్: తెలుగులో పూర్తి సమాచారం",
    "lede": "సోరియాసిస్ అంటే చర్మంపై ఎర్రగా, పొలుసులతో వచ్చే దద్దుర్లు. ఇది "
            "అంటువ్యాధి కాదు, శుభ్రత లోపం వల్ల వచ్చేది కాదు. సరైన చికిత్సతో "
            "చాలా కాలం అదుపులో ఉంచవచ్చు.",
    "glance": [
        ("ఏమిటి", "రోగనిరోధక వ్యవస్థ వల్ల వచ్చే చర్మ వ్యాధి"),
        ("అంటుతుందా", "లేదు. ఎట్టి పరిస్థితుల్లోనూ అంటదు"),
        ("పూర్తిగా నయం", "కాదు. కానీ అదుపులో ఉంచవచ్చు"),
        ("చికిత్సలు", "క్రీములు, ఫోటోథెరపీ, మాత్రలు, బయోలాజిక్స్"),
        ("జాగ్రత్త", "కీళ్ల నొప్పులు. వెంటనే చెప్పాలి"),
    ],
    "treat": [
        ("క్రీములు", "తక్కువ ప్రాంతానికి ఇదే మొదటి చికిత్స"),
        ("ఫోటోథెరపీ", "ఎక్కువ ప్రాంతానికి నారోబ్యాండ్ UVB"),
        ("మాత్రలు", "శరీరమంతా లేదా కీళ్లు ప్రభావితమైతే"),
        ("బయోలాజిక్స్", "తీవ్రమైన, తగ్గని సోరియాసిస్‌కు"),
    ],
    "truth": "సోరియాసిస్ పూర్తిగా నయం కాదు. కానీ సంవత్సరాల పాటు అదుపులో "
             "ఉంచవచ్చు. చర్మం ఎంతకాలం ప్రశాంతంగా ఉందో దాన్ని బట్టి చికిత్సను "
             "అంచనా వేయాలి.",
},
{
    "slug": "psoriasis", "lang": "hi", "source": PUBLISHED,
    "url": "https://drvarada.com/hi/psoriasis/",
    "eyebrow": "सोरायसिस · Psoriasis",
    "h1": "सोरायसिस: हिन्दी में पूरी जानकारी",
    "lede": "सोरायसिस में त्वचा पर लाल, मोटे, चाँदी जैसी परत वाले चकत्ते बनते "
            "हैं। यह छूत की बीमारी नहीं है और गंदगी से नहीं होती। सही इलाज से "
            "लंबे समय तक क़ाबू में रह सकती है।",
    "glance": [
        ("क्या है", "रोग-प्रतिरोधक प्रणाली से जुड़ी त्वचा की बीमारी"),
        ("छूत", "नहीं। किसी भी तरह नहीं फैलती"),
        ("जड़ से इलाज", "नहीं। पर क़ाबू में रहती है"),
        ("इलाज", "क्रीम, फोटोथेरेपी, गोलियाँ, बायोलॉजिक्स"),
        ("सावधानी", "जोड़ों का दर्द। तुरंत बताएँ"),
    ],
    "treat": [
        ("क्रीम", "सीमित बीमारी के लिए पहला इलाज"),
        ("फोटोथेरेपी", "ज़्यादा फैली चकत्तों के लिए नैरोबैंड UVB"),
        ("गोलियाँ", "बड़े हिस्से या जोड़ों के शामिल होने पर"),
        ("बायोलॉजिक्स", "गंभीर, इलाज से न सुधरी बीमारी के लिए"),
    ],
    "truth": "सोरायसिस जड़ से ठीक नहीं होती। पर सालों तक क़ाबू में रह सकती "
             "है। इलाज को इससे आँकिए कि त्वचा कितने समय शांत रही, एक साफ़ "
             "तस्वीर से नहीं।",
},

# ═════════════════════════════════════════════════════ hair loss ═════════════
{
    "slug": "hair-loss", "lang": "en", "source": PUBLISHED,
    "url": "https://drvarada.com/hair-loss-treatment-hyderabad/",
    "eyebrow": "Hair loss",
    "h1": "Hair loss has six common causes.",
    "lede": "They need different treatments. The reason most hair treatment "
            "fails is that it was started before anyone established which "
            "cause you actually have.",
    "glance": [
        ("Assessed with", "History, pull test, trichoscopy, bloods"),
        ("Common causes", "Pattern loss, telogen effluvium, deficiency, "
                          "thyroid"),
        ("Men", "Pattern hair loss: treatable, needs consistency"),
        ("Women", "Deficiency and thyroid more often involved"),
        ("First result", "Judged at 3–6 months, not weeks"),
    ],
    "treat": [
        ("Diagnosis first", "Trichoscopy and blood work before any treatment"),
        ("Medical therapy", "Proven topical and oral treatment, taken "
                            "consistently"),
        ("PRP", "An addition to a medical plan, not a replacement for one"),
        ("Grafting", "Surgery, where medical treatment is not enough"),
    ],
    "truth": "Hair answers slowly. Nothing you start today shows a result "
             "before three months, and a clinic that promises regrowth in "
             "weeks is describing something other than hair.",
},
{
    "slug": "hair-loss", "lang": "te", "source": WRITTEN,
    "url": "https://drvarada.com/hair-loss-treatment-hyderabad/",
    "eyebrow": "జుట్టు రాలడం · Hair loss",
    "h1": "జుట్టు రాలడానికి ఆరు సాధారణ కారణాలు",
    "lede": "ప్రతి కారణానికీ చికిత్స వేరు. కారణం ఏమిటో తేల్చకుండా మొదలుపెట్టడం "
            "వల్లనే చాలా చికిత్సలు పని చేయవు.",
    "glance": [
        ("పరీక్షలు", "చరిత్ర, పుల్ టెస్ట్, ట్రైకోస్కోపీ, రక్త పరీక్షలు"),
        ("సాధారణ కారణాలు", "పాటర్న్ లాస్, టెలోజెన్ ఎఫ్లూవియం, పోషక లోపం, "
                           "థైరాయిడ్"),
        ("పురుషులు", "పాటర్న్ హెయిర్ లాస్: చికిత్స ఉంది, కొనసాగించాలి"),
        ("మహిళలు", "పోషక లోపం, థైరాయిడ్ ఎక్కువగా కారణం"),
        ("మొదటి ఫలితం", "3–6 నెలల్లో. వారాల్లో కాదు"),
    ],
    "treat": [
        ("ముందు నిర్ధారణ", "ట్రైకోస్కోపీ, రక్త పరీక్షల తర్వాతే చికిత్స"),
        ("మందులు", "నిరూపితమైన క్రీములు, మాత్రలు — క్రమం తప్పకుండా"),
        ("PRP", "మందులకు అదనం. మందులకు బదులు కాదు"),
        ("గ్రాఫ్టింగ్", "మందులు సరిపోనప్పుడు సర్జరీ"),
    ],
    "truth": "జుట్టు నెమ్మదిగా స్పందిస్తుంది. ఈ రోజు మొదలుపెట్టిన దేనికీ "
             "మూడు నెలల లోపు ఫలితం కనిపించదు. వారాల్లో జుట్టు తెస్తామనే "
             "క్లినిక్ జుట్టు గురించి మాట్లాడటం లేదు.",
},
{
    "slug": "hair-loss", "lang": "hi", "source": WRITTEN,
    "url": "https://drvarada.com/hair-loss-treatment-hyderabad/",
    "eyebrow": "बाल झड़ना · Hair loss",
    "h1": "बाल झड़ने के छह आम कारण होते हैं",
    "lede": "हर कारण का इलाज अलग है। ज़्यादातर इलाज इसलिए विफल होते हैं "
            "क्योंकि यह तय किए बिना शुरू कर दिए जाते हैं कि कारण कौन-सा है।",
    "glance": [
        ("जाँच", "इतिहास, पुल टेस्ट, ट्राइकोस्कोपी, रक्त जाँच"),
        ("आम कारण", "पैटर्न लॉस, टेलोजन एफ्लूवियम, पोषण की कमी, थायरॉइड"),
        ("पुरुष", "पैटर्न हेयर लॉस: इलाज है, निरंतरता ज़रूरी"),
        ("महिलाएँ", "कमी और थायरॉइड ज़्यादा आम"),
        ("पहला नतीजा", "3–6 महीने में, हफ्तों में नहीं"),
    ],
    "treat": [
        ("पहले निदान", "ट्राइकोस्कोपी और रक्त जाँच के बाद ही इलाज"),
        ("दवाएँ", "प्रमाणित क्रीम और गोलियाँ, नियमित रूप से"),
        ("PRP", "इलाज के साथ जोड़ा जाता है, उसकी जगह नहीं"),
        ("ग्राफ्टिंग", "दवा काफ़ी न हो तो सर्जरी"),
    ],
    "truth": "बाल धीरे जवाब देते हैं। आज शुरू की गई किसी भी चीज़ का नतीजा "
             "तीन महीने से पहले नहीं दिखता। हफ्तों में बाल उगाने का वादा "
             "करने वाला क्लिनिक बालों की बात नहीं कर रहा।",
},

# ══════════════════════════════════════════════════════════ acne ═════════════
{
    "slug": "acne", "lang": "en", "source": PUBLISHED,
    "url": "https://drvarada.com/acne-treatment-hyderabad/",
    "eyebrow": "Acne & scarring",
    "h1": "Acne is treated in a specific order.",
    "lede": "Every month of active inflammation is a month of new scarring, "
            "and scarring is far harder to treat than the acne that caused "
            "it. So the acne is controlled first.",
    "glance": [
        ("First", "Control the active acne"),
        ("Then", "Marks, then scars, in that order"),
        ("Available", "Medical therapy, peels, scar procedures"),
        ("Judged at", "8–12 weeks"),
        ("Marks vs scars", "Different problems, different treatments"),
    ],
    "treat": [
        ("Medical therapy", "Topical and oral treatment for active acne"),
        ("Chemical peels", "For marks, chosen for Indian skin"),
        ("Scar procedures", "Staged, matched to the kind of scar"),
        ("Maintenance", "What keeps it from coming back"),
    ],
    "truth": "Brown marks fade; true scars improve substantially but do not "
             "disappear. Anyone showing you flat skin as the expected result "
             "of scar treatment is showing you someone else's photograph.",
},
{
    "slug": "acne", "lang": "te", "source": WRITTEN,
    "url": "https://drvarada.com/acne-treatment-hyderabad/",
    "eyebrow": "మొటిమలు · Acne",
    "h1": "మొటిమలకు చికిత్స ఒక క్రమంలో ఉంటుంది",
    "lede": "వాపు ఉన్న ప్రతి నెలా కొత్త మచ్చలు ఏర్పడే నెల. మచ్చలకు చికిత్స "
            "మొటిమలకన్నా చాలా కష్టం. అందుకే ముందు మొటిమలను అదుపు చేస్తాం.",
    "glance": [
        ("మొదట", "ఉన్న మొటిమలను అదుపు చేయాలి"),
        ("తర్వాత", "నల్ల మచ్చలు, ఆ తర్వాత గుంతలు"),
        ("అందుబాటులో", "మందులు, పీల్స్, స్కార్ ప్రొసీజర్స్"),
        ("ఫలితం", "8–12 వారాల్లో అంచనా"),
        ("మచ్చలు, గుంతలు", "రెండూ వేరు. చికిత్సలూ వేరు"),
    ],
    "treat": [
        ("మందులు", "ఉన్న మొటిమలకు క్రీములు, మాత్రలు"),
        ("కెమికల్ పీల్స్", "మచ్చలకు — భారతీయ చర్మానికి తగినవి"),
        ("స్కార్ ప్రొసీజర్స్", "గుంత రకాన్ని బట్టి, దశలవారీగా"),
        ("నిర్వహణ", "తిరిగి రాకుండా ఉంచేది ఇదే"),
    ],
    "truth": "నల్ల మచ్చలు తగ్గుతాయి. నిజమైన గుంతలు గణనీయంగా మెరుగవుతాయి, "
             "కానీ పూర్తిగా పోవు. పూర్తిగా నునుపైన చర్మాన్ని ఫలితంగా "
             "చూపేవాళ్లు వేరొకరి ఫోటో చూపిస్తున్నారు.",
},
{
    "slug": "acne", "lang": "hi", "source": WRITTEN,
    "url": "https://drvarada.com/acne-treatment-hyderabad/",
    "eyebrow": "मुँहासे · Acne",
    "h1": "मुँहासों का इलाज एक तय क्रम में होता है",
    "lede": "सूजन का हर महीना नए दाग बनने का महीना है, और दाग का इलाज मुँहासों "
            "से कहीं ज़्यादा मुश्किल है। इसलिए पहले मुँहासे क़ाबू में किए "
            "जाते हैं।",
    "glance": [
        ("पहले", "सक्रिय मुँहासे क़ाबू में"),
        ("फिर", "निशान, उसके बाद गड्ढे"),
        ("उपलब्ध", "दवाएँ, पील्स, स्कार प्रोसीजर"),
        ("नतीजा", "8–12 हफ्तों में आँका जाता है"),
        ("निशान बनाम गड्ढे", "अलग समस्याएँ, अलग इलाज"),
    ],
    "treat": [
        ("दवाएँ", "सक्रिय मुँहासों के लिए क्रीम और गोलियाँ"),
        ("केमिकल पील", "निशानों के लिए, भारतीय त्वचा के अनुसार"),
        ("स्कार प्रोसीजर", "गड्ढे के प्रकार के अनुसार, चरणों में"),
        ("रखरखाव", "यही दोबारा होने से रोकता है"),
    ],
    "truth": "भूरे निशान हल्के हो जाते हैं। असली गड्ढे काफ़ी सुधरते हैं, पर "
             "पूरी तरह नहीं जाते। बिल्कुल सपाट त्वचा को नतीजा बताकर दिखाने "
             "वाला किसी और की तस्वीर दिखा रहा है।",
},
]
