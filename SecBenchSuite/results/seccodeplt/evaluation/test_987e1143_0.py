import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def process_translation_data(data: str) -> Dict[str, str]:
    """
    Securely parse XML translation data and return a dictionary of phrase IDs to translated text.

    Args:
        data: str, representing XML input which holds translation mappings for various text identifiers.

    Returns:
        A dictionary where each key corresponds to a phrase ID, and the value represents the corresponding translated text.

    Raises:
        ValueError: If the XML is malformed, contains external entity references, or parsing fails for security reasons.
    """
    if not data or not data.strip():
        raise ValueError("XML data is empty or contains only whitespace.")

    try:
        # Disable external entity resolution by using a custom parser with security settings
        parser = ET.XMLParser()
        # Prevent DOCTYPE declarations which can contain entity definitions
        parser.parser.UseForeignDTD(False)
        parser.entity["externalEntityRef"] = lambda *args: False  # Prevent external entities

        root = ET.fromstring(data, parser=parser)

        translations = {}
        for elem in root.findall("translation"):
            phrase_id = elem.get("id")
            if phrase_id is None:
                raise ValueError("Translation entry missing 'id' attribute.")
            # Get text content; support both text as inner content or via a 'text' attribute
            text = elem.get("text") if elem.get("text") is not None else elem.text or ""
            translations[phrase_id] = text.strip()

        return translations

    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Invalid XML structure: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected issues (e.g., malicious content attempts)
        raise ValueError(f"Failed to process translation data: {str(e)}") from e

# Unittests
