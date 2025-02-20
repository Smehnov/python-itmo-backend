class TextProcessor:
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        if isinstance(text, dict):
            text = text.get('content', '')  # Get content from dict if it's a dict
        return len(text.split())

    @staticmethod
    def count_chars(text: str) -> int:
        """Count characters in text."""
        if isinstance(text, dict):
            text = text.get('content', '')
        return len(text)

    @staticmethod
    def process_text(text: str) -> dict:
        """Process text and return statistics."""
        if isinstance(text, dict):
            text = text.get('content', '')
        return {
            'words': TextProcessor.count_words(text),
            'chars': TextProcessor.count_chars(text)
        }

    @staticmethod
    def generate_description(text: str) -> str:
        """Generate human-readable description from text."""
        if isinstance(text, dict):
            text = text.get('content', '')
        stats = TextProcessor.process_text(text)
        return f"Document contains {stats['words']} words and {stats['chars']} characters" 