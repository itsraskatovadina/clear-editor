from core.models.html_editor_model import TagCompletionsModel


def test_default_tags():
    m = TagCompletionsModel()
    assert len(m.tags) == 16
    assert "p" in m.tags
    assert "div" in m.tags
    assert "table" in m.tags
    print("  OK default tags")


def test_is_valid_tag():
    m = TagCompletionsModel()
    assert m.is_valid_tag("div") is True
    assert m.is_valid_tag("span") is True
    assert m.is_valid_tag("xyz") is False
    assert m.is_valid_tag("") is False
    print("  OK is_valid_tag")


def test_add_tag():
    m = TagCompletionsModel()
    m.add("article")
    assert "article" in m.tags
    assert m.is_valid_tag("article") is True
    m.add("article")
    assert m.tags.count("article") == 1
    print("  OK add tag")


def test_remove_tag():
    m = TagCompletionsModel()
    m.remove("p")
    assert "p" not in m.tags
    assert m.is_valid_tag("p") is False
    m.remove("p")
    print("  OK remove tag")


def test_custom_initial_tags():
    m = TagCompletionsModel(tags=["foo", "bar"])
    assert m.tags == ["foo", "bar"]
    assert m.is_valid_tag("foo") is True
    assert m.is_valid_tag("p") is False
    print("  OK custom initial tags")


def test_tags_returns_copy():
    m = TagCompletionsModel()
    tags = m.tags
    tags.append("hack")
    assert "hack" not in m.tags
    print("  OK tags returns copy")


if __name__ == "__main__":
    test_default_tags()
    test_is_valid_tag()
    test_add_tag()
    test_remove_tag()
    test_custom_initial_tags()
    test_tags_returns_copy()
    print("\nAll TagCompletionsModel tests passed.")
