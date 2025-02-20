import pytest
from src.app.services.text_processor import TextProcessor

@pytest.fixture
def processor():
    return TextProcessor()

def test_count_words(processor):
    assert processor.count_words("Hello world! This is a test.") == 6
    assert processor.count_words("") == 0
    assert processor.count_words("One") == 1

def test_count_chars(processor):
    assert processor.count_chars("Hello world!") == 12
    assert processor.count_chars("") == 0
    assert processor.count_chars("A") == 1

def test_generate_description(processor):
    text = "This is a test text with six words"
    # Count actual words and characters
    words = len(text.split())
    chars = len(text)
    expected = f"Document contains {words} words and {chars} characters"
    assert processor.generate_description(text) == expected

def test_process_text(processor):
    text = "Hello world! This is a test."
    result = processor.process_text(text)
    assert result["words"] == 6
    assert result["chars"] == 28