import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def safe_translation_xml(xml_input: str) -> Dict[str, str]:
    """
    Safely parse XML input containing translation data, preventing external entity resolution.

    Args:
        xml_input: str, the XML input containing translations associated with various text identifiers.

    Returns:
        A dictionary where the keys represent translation phrase IDs and the corresponding values are the translations.

    Raises:
        ValueError: If the XML input is improperly structured or contains external entity declarations.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_input, str):
        raise TypeError("XML input must be a string")

    if not xml_input.strip():
        raise ValueError("XML input cannot be empty")

    # Configure secure parsing by using defusedxml or secure ElementTree practices
    # Since defusedxml is not in standard library, we use ElementTree with precautions
    # and manually check for potential external entity patterns in DOCTYPE

    # Check for DOCTYPE declaration which may contain external entities
    stripped_input = xml_input.strip()
    if '<!DOCTYPE' in stripped_input.upper():
        raise ValueError("DOCTYPE declarations are not allowed to prevent XXE attacks")

    if '<!ENTITY' in stripped_input.upper():
        raise ValueError("ENTITY declarations are not allowed to prevent XXE attacks")

    try:
        # Use ElementTree with security in mind
        # Disable default parser behavior that might resolve entities
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity.update({
            'lt': '<',
            'gt': '>',
            'amp': '&',
            'quot': '"',
            'apos': "'"
        })
        
        root = ET.fromstring(xml_input, parser=parser)
        
        translations = {}
        
        # Assuming XML structure like:
        # <translations>
        #   <translation id="greeting">Hello</translation>
        # </translations>
        for elem in root.findall('.//translation'):
            phrase_id = elem.get('id')
            if phrase_id is None:
                continue
            translation = elem.text or ""
            translations[phrase_id] = translation
            
        return translations
        
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}")
    except ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        # Catch any other unexpected XML-related exceptions
        raise ValueError(f"Error processing XML: {str(e)}")