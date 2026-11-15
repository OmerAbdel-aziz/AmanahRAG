from worker.chunking import chunk_text, normalize_for_embedding


def test_empty_text_yields_no_chunks() -> None:
    assert chunk_text("   \n  ") == []


def test_short_text_is_one_chunk() -> None:
    chunks = chunk_text("A short policy note.", 220, 40)

    assert len(chunks) == 1
    assert chunks[0].ordinal == 0
    assert chunks[0].token_count == 4


def test_long_text_overlaps_and_keeps_order() -> None:
    text = " ".join(f"word{i}" for i in range(1000))
    chunks = chunk_text(text, max_words=200, overlap_words=25)

    assert len(chunks) > 1
    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.text.split()[0] for chunk in chunks)
    # Consecutive windows share tokens.
    first = set(chunks[0].text.split())
    second = set(chunks[1].text.split())
    assert first & second


def test_overlap_larger_than_window_is_rejected() -> None:
    try:
        chunk_text("one two three", 10, 10)
    except ValueError as error:
        assert "overlap" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_arabic_normalisation_strips_diacritics_and_tatweel() -> None:
    raw = "الْأَمَـانَة"
    assert normalize_for_embedding(raw) == "الامانة"
