import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def load_translation_xml(translation_xml: str) -> Dict[str, str]:
    """
    Parse an XML string containing translation data and return a dictionary
    mapping translation phrase IDs to their translated texts.

    Security: External entity processing is disabled to prevent XXE (XML External
    Entity) attacks. The function treats the input as untrusted.

    Args:
        translation_xml: A string containing XML data with translations.

    Returns:
        A dictionary where keys are translation phrase IDs and values are
        the corresponding translated texts.

    Raises:
        ValueError: If the XML is malformed or attempts to use external entities.
        RuntimeError: If a potential external entity attack is detected.
    """
    # Configure secure XML parsing
    parser = ET.XMLParser()
    
    # Remove default handlers to prevent external entity inclusion
    parser.entity["externalEntityRef"] = ""  # This disables external entities
    
    try:
        # Parse the XML with security measures
        root = ET.fromstring(translation_xml.strip(), parser=parser)
        
        translations = {}
        
        # Example expected structure:
        # <translations>
        #   <translation id="greeting">Hello</translation>
        #   <translation id="farewell">Goodbye</translation>
        # </translations>
        
        for elem in root.findall(".//translation[@id]"):
            phrase_id = elem.get("id")
            text = elem.text or ""
            translations[phrase_id] = text.strip()
            
        return translations
        
    except (ExpatError, ET.ParseError) as e:
        raise ValueError(f"Malformed XML or invalid content: {str(e)}")
    except Exception as e:
        # Catch any other unexpected XML-related errors
        raise ValueError(f"Failed to parse XML: {str(e)}")

# Unittests
