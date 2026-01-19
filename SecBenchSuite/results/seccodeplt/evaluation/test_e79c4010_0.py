import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def secure_translation_parser(xml_data: str) -> Dict[str, str]:
    """
    Safely parses XML data containing translations and returns a dictionary
    mapping translation IDs to their corresponding text. The parser is configured
    to prevent external entity resolution to mitigate security risks from untrusted sources.

    Args:
        xml_data: str, the XML input containing translations associated with various text identifiers.

    Returns:
        A dictionary where the keys represent translation phrase IDs and the values are the translations.

    Raises:
        ValueError: If the XML is malformed, improperly structured, or contains external entity declarations.
        RuntimeError: If any other parsing error occurs due to security restrictions.
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("XML input is empty or contains only whitespace.")

    # Configure parser with security in mind
    parser = ET.XMLParser()
    
    # Disable DTD processing entirely to prevent external entity attacks
    # This is the most effective way to block XXE (XML External Entity) attacks
    parser.parser.UseForeignDTD = False
    parser.entity["external_parameter_entity"] = None
    parser.entity["parameter_entity"] = None
    parser.entity["external_general_entity"] = None

    try:
        root = ET.fromstring(xml_data.strip(), parser=parser)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML data: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing failed: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected parser-related exceptions
        raise RuntimeError(f"Unexpected error during XML parsing: {str(e)}") from e

    # Validate root element (basic structure check)
    if root.tag != 'translations' and 'translation' not in root.tag.lower():
        raise ValueError("Root element must be a translations container.")

    result = {}
    for element in root:
        # Expect elements to have an 'id' or 'key' attribute
        phrase_id = element.get('id') or element.get('key')
        if phrase_id is None:
            raise ValueError(f"Translation entry missing 'id' or 'key' attribute: {ET.tostring(element, encoding='unicode')}")

        # Extract text content
        translation = element.text or ""
        
        # Normalize whitespace
        translation = translation.strip()

        if phrase_id in result:
            raise ValueError(f"Duplicate translation ID found: {phrase_id}")

        result[phrase_id] = translation

    return result

# Unittests
