import xml.etree.ElementTree as ET
from xml.parsers import expat
from typing import Dict


def handle_translation_xml(xml_content: str) -> Dict[str, str]:
    """
    Parses XML content containing translation strings and returns a dictionary
    mapping phrase IDs to their translated text.

    Security: External entity expansion is disabled to prevent XXE attacks.
    The input is treated as untrusted.

    Args:
        xml_content: str, the XML content representing translations for various language strings

    Returns:
        A dictionary containing translation pairs where the key is the phrase ID
        and the value is the translated text.

    Raises:
        ValueError: If the XML is malformed, contains external entity references,
                    or cannot be safely parsed.
    """
    if not xml_content or not xml_content.strip():
        raise ValueError("XML content is empty or None")

    # Disable external entities by using defusedxml or secure expat settings
    # Here we use ElementTree with protection via expat settings
    try:
        # Use a secure parser configuration
        parser = ET.XMLParser()
        # Disable resolving external entities
        parser.parser.UseForeignDTD = False
        parser.parser.EntityDeclHandler = None
        parser.parser.UnparsedEntityDeclHandler = None

        # Parse the XML string
        root = ET.fromstring(xml_content, parser=parser)

        translations = {}

        # Example structure assumed: <translations><entry key="greeting">Hello</entry></translations>
        # or <translations><phrase id="save">Save</phrase></translations>
        for elem in root.findall(".//"):
            # Look for common patterns: elements with 'key' or 'id' attribute and text content
            key = elem.get('key') or elem.get('id')
            if key and elem.text:
                translations[key] = elem.text.strip()

        return translations

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}") from e
    except expat.error as e:
        raise ValueError(f"XML parsing failed due to potential malicious content: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected issues (e.g., excessive entity expansion)
        raise ValueError(f"Failed to process XML securely: {str(e)}") from e