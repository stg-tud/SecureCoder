import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def process_translations_xml(xml_payload: str) -> Dict[str, str]:
    """
    Parses XML translation data and returns a dictionary of translation IDs to their translated texts.
    
    Security: External entity processing is disabled to prevent XXE (XML External Entity) attacks.
    The function treats all input as untrusted and raises an error on malformed XML or attempted
    external entity resolution.

    Args:
        xml_payload (str): XML string containing translations for multiple language identifiers.

    Returns:
        Dict[str, str]: A dictionary where keys are translation phrase IDs and values are the 
                       corresponding translated texts.

    Raises:
        ValueError: If the XML is malformed or contains attempts to use external entities.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_payload, str):
        raise TypeError("xml_payload must be a string")

    if not xml_payload.strip():
        raise ValueError("xml_payload cannot be empty")

    try:
        # Parse XML with default parser settings (ElementTree does not process external entities by default)
        # However, we wrap parsing in a way that prevents potential exploits
        parser = ET.XMLParser()
        # Explicitly disable DTD loading to prevent external entity inclusion
        parser.parser.UseForeignDTD = False
        parser.parser.EntityDeclHandler = None
        parser.parser.UnparsedEntityDeclHandler = None

        root = ET.fromstring(xml_payload, parser=parser)

        translations = {}
        
        # Assuming a structure like:
        # <translations>
        #   <translation id="greeting">Hello</translation>
        #   <translation id="farewell">Goodbye</translation>
        # </translations>
        for elem in root.findall(".//translation"):
            trans_id = elem.get("id")
            if trans_id is not None:
                # Get text content, default to empty string if None
                text = elem.text or ""
                translations[trans_id] = text

        return translations

    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Malformed XML or invalid content: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected XML processing issues
        raise ValueError(f"Error processing XML: {str(e)}") from e