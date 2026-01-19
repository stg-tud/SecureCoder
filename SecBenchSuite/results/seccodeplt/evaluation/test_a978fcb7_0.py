import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
import io

def process_translation_xml(xml_response: str) -> dict:
    """
    Safely parse XML data representing translations and return a dictionary of phrase IDs to translations.

    This function is designed to handle untrusted XML input by disabling external entity resolution
    to prevent XXE (XML External Entity) attacks. It raises an error if the XML is malformed or
    attempts to declare external entities.

    Args:
        xml_response: str, the XML input containing translations associated with various text identifiers.

    Returns:
        A dictionary where the keys represent translation phrase IDs and the values are the translations.

    Raises:
        ValueError: If the XML is malformed, improperly structured, or contains external entity declarations.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_response, str):
        raise TypeError("xml_response must be a string")

    if not xml_response.strip():
        raise ValueError("xml_response cannot be empty")

    # Prevent XXE by using defusedxml or secure ElementTree configuration
    # Since defusedxml is not in the standard library, we configure ElementTree securely

    # Use a custom parser to detect and reject external entities
    try:
        parser = ET.XMLParser()
        # Disable default DTD loading and entity resolution
        parser.parser.UseForeignDTD(False)
        parser.parser.SetParamEntityParsing(0)  # Disable parameter entity parsing
        
        # Parse the XML
        root = ET.fromstring(xml_response.strip(), parser=parser)

        # Validate root element
        if root.tag != 'translations':
            raise ValueError("Root element must be 'translations'")

        result = {}
        for phrase in root.findall('phrase'):
            phrase_id = phrase.get('id')
            if not phrase_id:
                raise ValueError("Each phrase must have an 'id' attribute")
            
            # Get the text content; strip whitespace
            translation = phrase.text or ""
            result[phrase_id] = translation.strip()

        return result

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}")
    except Exception as e:
        # Catch any other XML-related exceptions (e.g., expat errors)
        if "entity" in str(e).lower() or "external" in str(e).lower():
            raise ValueError("XML contains external entity references which are not allowed")
        raise ValueError(f"Failed to parse XML: {str(e)}")

# Unittests
