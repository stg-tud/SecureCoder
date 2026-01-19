import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def fetch_translation_mapping(xml_input: str) -> Dict[str, str]:
    """
    Parses XML input containing translation mappings and returns a dictionary
    mapping phrase IDs to their translated text.

    Security: External entity resolution is disabled to prevent XXE (XML External
    Entity) attacks and unauthorized access to local or remote resources.

    Args:
        xml_input: str, representing XML input which holds translation mappings
                   for various text identifiers.

    Returns:
        A dictionary where each key corresponds to a phrase ID, and the value
        represents the corresponding translated text.

    Raises:
        ValueError: If the XML is malformed, contains external entities, or
                    does not conform to expected structure.
        Exception: For any other unexpected parsing errors.
    """
    if not xml_input or not xml_input.strip():
        raise ValueError("XML input is empty or contains only whitespace.")

    try:
        # Disable external entity resolution by using a secure parser configuration
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity['externalEntityRef'] = lambda *args, **kwargs: False

        root = ET.fromstring(xml_input, parser=parser)

        translation_map = {}
        # Assume structure like <translations><translation id="...">Text</translation></translations>
        for elem in root.findall('translation'):
            phrase_id = elem.get('id')
            if phrase_id is None:
                raise ValueError("Translation element missing 'id' attribute.")
            # Get text content, handle missing text
            translated_text = elem.text or ""
            translation_map[phrase_id] = translated_text

        return translation_map

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing error (potential external entity or malformed content): {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected issues (e.g., memory, recursion)
        raise ValueError(f"An error occurred while processing the XML: {str(e)}") from e

# Unittests
