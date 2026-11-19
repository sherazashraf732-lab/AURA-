"""Language and style detection for English, Urdu (Arabic script), Roman Urdu and mixes.

No off-the-shelf detector supports Roman Urdu (verified in Phase 1 for lingua-py), so AURA uses:
1. Unicode script counting (Arabic-script Urdu vs Latin),
2. a Roman Urdu lexicon score over Latin words,
3. the model itself as the final judge, via a reply-style instruction built from this result.
"""

import re
from dataclasses import dataclass
from typing import Literal

Lang = Literal["en", "ur", "ur-Latn", "mixed", "unknown"]

# High-frequency Roman Urdu function words and common verbs/particles. Words that are also common
# English words ("me", "to", "hi", "is", "us", "par") are deliberately excluded to avoid false hits.
ROMAN_URDU = frozenset(
    """
    hai hain hy hyn tha thi thay thy ho hoga hogi hongay raha rahi rahe rha rhi kya kia kyun
    kyon kyunke kyunki kaise kaisay kese kaisa kaisi kahan kidhar kab kaun kon kitna kitni
    nahi nahin nai nhi na mein mai mujhe mujhay mjhe mera meri mere hum hamara hamari humein
    tum tumhara tumhari aap ap apka apki apke apna apni apne woh wo yeh ye inhon unhon unka
    unki uska uski iska iski ka ki ke ko se sey say bhi bhe aur lekin magar phir sirf bas abhi
    ab agar ek jo jis jise karo karna karta karti karte kar kare karein kiya kiye kaam haal
    krna kro krta krti dekho dekhna batao bataen bata chahiye chahye chahta chahti sakta sakti
    sakte samajh samjha samjhao likho likhna parho acha accha achha theek thik sahi galat
    bohat bahut bht zyada kam thora thoda shukriya meharbani jee ji haan han bilkul yaar bhai
    behen dost kuch koi sab sabhi yahan wahan idhar udhar aaj kal parson subah shaam raat din
    """.split()
)

ENGLISH_FUNCTION = frozenset(
    "the a an and or but of to for with are was were be this that these those what how why "
    "when where which who can could would should will you your i we they it please".split()
)

_WORD = re.compile(r"[A-Za-z']+")
_ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
_LATIN = re.compile(r"[A-Za-z]")
_CODE = re.compile(r"```.*?```|`[^`]*`|https?://\S+", re.S)


@dataclass(frozen=True)
class Detection:
    language: Lang
    script: Literal["arabic", "latin", "mixed", "none"]
    roman_urdu_ratio: float
    formal: bool

    def reply_instruction(self) -> str:
        style = "formal and respectful" if self.formal else "natural and conversational"
        return {
            "en": f"Reply in English. Keep the tone {style}.",
            "ur": f"Reply in Urdu using Urdu (Arabic) script. Keep the tone {style}.",
            "ur-Latn": (
                "Reply in Roman Urdu (Urdu written in Latin letters, as the user writes). "
                f"Do not switch to Urdu script or full English. Keep the tone {style}."
            ),
            "mixed": (
                "The user mixes Urdu and English. Reply in the same mix and script the user uses. "
                f"Keep the tone {style}."
            ),
            "unknown": "Reply in the language the user wrote in.",
        }[self.language] + " Keep code, names and technical terms unchanged."


_FORMAL_MARKERS = frozenset(
    "aap apka apki apke janab sahib meharbani please kindly sir madam".split()
)


def detect(text: str) -> Detection:
    plain = _CODE.sub(" ", text)
    arabic = len(_ARABIC.findall(plain))
    latin = len(_LATIN.findall(plain))
    words = [w.lower() for w in _WORD.findall(plain)]
    ru_hits = sum(1 for w in words if w in ROMAN_URDU)
    ratio = ru_hits / len(words) if words else 0.0
    formal = any(w in _FORMAL_MARKERS for w in words) or "آپ" in plain

    total = arabic + latin
    if total == 0:
        return Detection("unknown", "none", 0.0, formal)
    arabic_share = arabic / total
    if arabic_share >= 0.8:
        return Detection("ur", "arabic", ratio, formal)
    if arabic_share >= 0.2:
        return Detection("mixed", "mixed", ratio, formal)

    # Latin script only. Roman Urdu borrows English nouns freely ("mera code"), so English
    # *function* words signal a real mix. "is"/"in" are excluded: Urdu "is" means "this".
    en_hits = sum(1 for w in words if w in ENGLISH_FUNCTION)
    if ru_hits and en_hits and ratio >= 0.1:
        return Detection("mixed", "latin", ratio, formal)
    if ru_hits and ratio >= 0.25:
        return Detection("ur-Latn", "latin", ratio, formal)
    return Detection("en", "latin", ratio, formal)


def resolve(text: str, account_override: str | None, chat_override: str | None) -> Detection:
    """Explicit preferences win: chat override, then account override, then detection."""
    d = detect(text)
    forced = chat_override or account_override
    if forced in ("en", "ur", "ur-Latn"):
        return Detection(forced, d.script, d.roman_urdu_ratio, d.formal)  # type: ignore[arg-type]
    return d
