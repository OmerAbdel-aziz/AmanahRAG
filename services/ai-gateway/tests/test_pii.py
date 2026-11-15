from app.pii import PIIScrubber


def test_scrubs_email_and_restores_it() -> None:
    scrubber = PIIScrubber()
    result = scrubber.scrub("Write to sara.ahmed@example.org about the refund.")

    assert "sara.ahmed@example.org" not in result.text
    assert "[EMAIL_1]" in result.text
    assert scrubber.restore(result.text, result.mapping) == (
        "Write to sara.ahmed@example.org about the refund."
    )


def test_scrubs_multiple_categories_without_collisions() -> None:
    scrubber = PIIScrubber()
    result = scrubber.scrub(
        "Call +971 50 123 4567 or email ops@amanah.test. IBAN AE07 0331 2345 6789 0123 456."
    )

    assert "ops@amanah.test" not in result.text
    assert "123 4567" not in result.text
    assert result.mapping
    restored = scrubber.restore(result.text, result.mapping)
    assert "ops@amanah.test" in restored
    assert "+971 50 123 4567" in restored


def test_scrub_payload_walks_nested_json() -> None:
    scrubber = PIIScrubber()
    payload = {
        "question": "Contact me at a@b.co",
        "messages": [{"content": "My number is 0501234567"}],
        "keep": 7,
    }

    cleaned, mapping = scrubber.scrub_payload(payload)

    assert cleaned["keep"] == 7
    assert "a@b.co" not in str(cleaned)
    assert mapping


def test_restore_is_order_independent() -> None:
    scrubber = PIIScrubber()
    mapping = {"[EMAIL_1]": "a@b.co", "[EMAIL_10]": "ten@b.co"}
    text = "first [EMAIL_10] then [EMAIL_1]"
    assert scrubber.restore(text, mapping) == "first ten@b.co then a@b.co"
