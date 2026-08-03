"""Consultation fees — written once, placed on every page that needs them.

WHY THIS IS A FUNCTION AND NOT A CONSTANT
  Seven pages carry this block. If it were a module-level dict they would all
  share one object, and anything that ever mutated a section in place would
  change it on the other six pages at once — the kind of bug that shows up as
  "why does the psoriasis page say something the vitiligo page doesn't". Each
  call returns a fresh dict.

WHY THE FEE IS PUBLISHED WHEN TREATMENT COSTS ARE NOT
  The cost pages argue at length that rupee figures for treatment are withheld
  on purpose: the number of sessions your patches need depends on the diagnosis,
  so a price quoted before an examination is an advertisement rather than
  information. The consultation fee is the opposite case. It is fixed, it is the
  same for everyone, it is knowable before anyone examines anything, and it is
  the one number a patient needs in order to decide whether to start at all.
  Publishing it follows the same principle that withholds the others.

  Which is why `note_cost` exists: on a cost page the block has to say that
  distinction out loud, or the page reads as though it contradicts itself.
"""

from chrome import (FEE_CLINIC_SHOW, FEE_DIFF_SHOW, FEE_ONLINE_SHOW, FEE_TAX)

# Said in one voice everywhere. The difference-only rule is the part patients
# are most likely to be surprised by later, so it is in the note on every
# placement rather than only on the online pages.
NOTE = (
    f"Fees are for the consultation itself. Where an online consultation turns out "
    f"to need an examination in person, only the difference of {FEE_DIFF_SHOW} {FEE_TAX} "
    f"is charged, not a second full fee. Medication, tests and procedures are "
    f"separate and are quoted after examination, in writing."
)

NOTE_COST = (
    f"The consultation fee is published because it is fixed and the same for "
    f"everyone. Treatment figures on this page are not, and that is deliberate: "
    f"what a course costs depends on the diagnosis, so a number quoted before an "
    f"examination would be an advertisement rather than information. Where an "
    f"online consultation turns out to need an examination in person, only the "
    f"difference of {FEE_DIFF_SHOW} {FEE_TAX} is charged."
)

ONLINE_ITEM = {
    "eyebrow": "Anywhere in India",
    "title": "Online video consultation",
    "price": FEE_ONLINE_SHOW,
    "tax": FEE_TAX,
    "body": "History and photographs are taken on WhatsApp first, so the doctor has "
            "read your case before the call begins rather than during it.",
    "list": [
        "Paid in advance, then you choose a date from the open slots",
        "In English, Telugu or Hindi",
        "Diagnosis and plan sent back to you in writing",
        "Follow-up questions on the same WhatsApp thread",
    ],
}

CLINIC_ITEM = {
    "eyebrow": "At the clinic, Secunderabad",
    "title": "In-person appointment",
    "price": FEE_CLINIC_SHOW,
    "tax": FEE_TAX,
    "body": "The full examination, including the two instruments that cannot travel "
            "over video: the Wood's lamp and the dermatoscope.",
    "list": [
        "Booked on WhatsApp; a time is confirmed back to you",
        "Bring previous prescriptions and any recent reports",
        "Only the difference is charged after an online consult",
        "Procedures are quoted separately, after examination",
    ],
}


def fees_block(eyebrow: str = "Consultation fees",
               h2: str = "What a consultation costs",
               intro: str | None = None,
               note: str = NOTE,
               online_first: bool = True) -> dict:
    """A fresh fees section. `online_first` puts the relevant one first: a
    reader on the clinic page wants the in-person fee at the top of the pair."""
    items = [ONLINE_ITEM, CLINIC_ITEM] if online_first else [CLINIC_ITEM, ONLINE_ITEM]
    section = {"kind": "fees", "anchor": "fees", "eyebrow": eyebrow, "h2": h2,
               "items": [dict(i) for i in items], "note": note}
    if intro:
        section["intro"] = intro
    return section


# The fee questions, asked the way patients ask them. Placed on the pages whose
# FAQ block a patient reaches while deciding, not on all sixty-one.
FEE_FAQS = [
    ("What does a consultation cost?",
     f"An online video consultation is {FEE_ONLINE_SHOW} {FEE_TAX}. An in-person "
     f"appointment at the clinic in Secunderabad is {FEE_CLINIC_SHOW} {FEE_TAX}. "
     f"Both cover the consultation itself; medication, tests and procedures are "
     f"separate and are quoted after examination."),
    ("Do I pay before or after an online consultation?",
     "Before. Send your history and photographs on WhatsApp, settle the fee, and "
     "you then choose a date from the slots that are open. Paying in advance is "
     "what holds the slot — it is a video appointment with a doctor, not a "
     "callback queue."),
    ("If I consult online and then have to come in, do I pay twice?",
     f"No. Only the difference of {FEE_DIFF_SHOW} {FEE_TAX} is charged. Being told "
     f"a video consultation cannot settle your problem is a legitimate outcome, "
     f"and you should not be charged twice for finding that out."),
]
