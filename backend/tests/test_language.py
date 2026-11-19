import pytest

from app.modules.language import detect, resolve

CASES = [
    # English
    ("Can you summarize this article for me?", "en"),
    ("What is the capital of France", "en"),
    ("hi", "en"),
    ("Please fix the bug in `kya_value = 1`", "en"),  # code is ignored
    # Urdu (Arabic script)
    ("آپ کیسے ہیں؟", "ur"),
    ("مجھے اس مضمون کا خلاصہ چاہیے", "ur"),
    # Roman Urdu
    ("aap kaise hain", "ur-Latn"),
    ("mujhe is article ka summary chahiye", "ur-Latn"),
    ("kya haal hai", "ur-Latn"),
    ("theek hai", "ur-Latn"),
    ("yaar mera code kaam nahi kar raha", "ur-Latn"),
    ("shukriya", "ur-Latn"),
    # Mixed
    ("Mujhe ek Python function chahiye jo CSV file read kare and plot a chart", "mixed"),
    ("Please explain machine learning مجھے سمجھائیں", "mixed"),
    ("Can you batao how to deploy this app on Vercel", "mixed"),
]


@pytest.mark.parametrize(("text", "expected"), CASES)
def test_detect(text: str, expected: str) -> None:
    assert detect(text).language == expected


def test_formality() -> None:
    assert detect("aap kaise hain").formal is True
    assert detect("tum kya kar rahe ho").formal is False


def test_overrides_win() -> None:
    assert resolve("hello there", "ur-Latn", None).language == "ur-Latn"
    assert resolve("hello there", "ur-Latn", "en").language == "en"
    assert resolve("aap kaise hain", None, None).language == "ur-Latn"


def test_instruction_mentions_script() -> None:
    assert "Roman Urdu" in detect("kya haal hai").reply_instruction()
    assert "Urdu (Arabic) script" in detect("آپ کیسے ہیں").reply_instruction()


def test_empty_and_symbols() -> None:
    assert detect("").language == "unknown"
    assert detect("🙂 123 !!").language == "unknown"
