# Asking patients for a Google review — WhatsApp messages

Forwardable text in English, Telugu and Hindi. The brand names are the exact
strings from `signage/board.py` (`TELUGU` / `HINDI`), so the message, the
board on the building and the site all say the practice's name the same way.

## The link

    https://g.page/r/CQmLVdnUqPhuEAI/review

Google's own short review link. Verified 2026-08-04 by decoding it: the payload
is a protobuf fixed64 carrying `6ef8a8d4d9558b09` little-endian —
**7996326770529110793**, which is `GOOGLE_CID` in `chrome.py`. It opens the
review box on the CORRECT listing, not the dead "BNR Skin and Vitiligo Centre"
duplicate six metres away.

It is shorter and more forwardable than the `search.google.com/local/writereview`
form in `chrome.py`, which is why it is the one used in messages.

---

## English

> 🙏 Thank you for visiting *Dr. Varada's Skin & Hair Center* (formerly BNR
> Skin & Vitiligo Hospital), Karkhana.
>
> If you have a minute, would you leave a review on Google? It helps other
> people looking for skin and hair treatment find the clinic.
>
> Tap here, choose your rating and write a line or two:
> https://g.page/r/CQmLVdnUqPhuEAI/review
>
> Thank you,
> Dr. (Lt Col) Khagendra Varada

## తెలుగు

> 🙏 *డా. వరద స్కిన్ అండ్ హెయిర్ సెంటర్* (గతంలో BNR స్కిన్ అండ్ విటిలిగో
> హాస్పిటల్), కార్ఖానాకు వచ్చినందుకు ధన్యవాదాలు.
>
> మీకు ఒక్క నిమిషం సమయం ఉంటే, గూగుల్‌లో మీ అభిప్రాయం రాస్తారా? చర్మ, జుట్టు
> చికిత్స కోసం వెతుకుతున్న ఇతరులకు క్లినిక్ కనిపించడానికి ఇది సహాయపడుతుంది.
>
> ఇక్కడ నొక్కి, రేటింగ్ ఇచ్చి, రెండు మాటలు రాయండి:
> https://g.page/r/CQmLVdnUqPhuEAI/review
>
> ధన్యవాదాలు,
> డా. (లెఫ్టినెంట్ కల్నల్) ఖగేంద్ర వరద

## हिन्दी

> 🙏 *डॉ. वरदा स्किन एंड हेयर सेंटर* (पहले BNR स्किन एंड विटिलिगो हॉस्पिटल),
> करखाना आने के लिए धन्यवाद।
>
> अगर आपके पास एक मिनट हो, तो क्या आप गूगल पर अपनी राय लिखेंगे? इससे त्वचा और
> बालों का इलाज ढूँढ रहे दूसरे लोगों को क्लिनिक मिलने में मदद मिलती है।
>
> यहाँ टैप करें, रेटिंग दें और दो पंक्तियाँ लिखें:
> https://g.page/r/CQmLVdnUqPhuEAI/review
>
> धन्यवाद,
> डॉ. (ले. कर्नल) खगेंद्र वरदा

---

## Short version, if the long one feels like too much

> 🙏 Thank you for visiting Dr. Varada's Skin & Hair Center. If you have a
> minute, a review on Google helps other patients find us:
> https://g.page/r/CQmLVdnUqPhuEAI/review

> 🙏 డా. వరద స్కిన్ అండ్ హెయిర్ సెంటర్‌కు వచ్చినందుకు ధన్యవాదాలు. ఒక్క నిమిషం
> ఉంటే, గూగుల్‌లో మీ అభిప్రాయం ఇతర రోగులకు క్లినిక్ కనిపించడానికి సహాయపడుతుంది:
> https://g.page/r/CQmLVdnUqPhuEAI/review

---

## Rules that protect the reviews you already have

**Never offer anything in return.** No discount, no free follow-up, no
priority slot. It violates Google's policy and the NMC advertising code, and
the penalty is not a warning — it is the removal of reviews, which costs the
31 already earned.

**Send it to everyone, not only the patients you expect to be pleased.**
Filtering for likely-positive reviewers is "review gating" and is explicitly
against Google's policy. It is also self-defeating: a wall of five stars with
no middle reads as bought, and 4.6 is more persuasive than 5.0.

**Do not hand a patient a device in the clinic to review on.** Multiple
reviews from one device or one IP are the clearest automated-filter signal
there is, and they get removed silently — the review appears to post and then
is simply not there. Send the link; let them write it on their own phone,
in their own time.

**A steady trickle, not a burst.** Thirty reviews in a week after a year of
none is a pattern Google's systems are built to catch. A few a week, sent
after visits, is both safer and better: recency is itself a ranking factor.

**Reply to every review, including the unhappy ones.** A calm, specific,
non-defensive reply to a complaint persuades more readers than the complaint
dissuades — and never discuss a patient's clinical details in a public reply.

**Send it the day after the visit,** not on the way out. People write more
considered reviews once they have got home, and it does not feel transactional.
