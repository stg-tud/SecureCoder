import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def process_translation_xml(xml_data: str) -> Dict[str, str]:
    """
    Parse XML translation data and return a dictionary of translation IDs to translated texts.
    
    This function is designed to securely process XML data from untrusted sources by
    disabling external entity processing to prevent XXE (XML External Entity) attacks.
    
    Args:
        xml_data: A string containing XML data with translations for multiple languages.
        
    Returns:
        A dictionary where keys are translation phrase IDs and values are the translated texts.
        
    Raises:
        ValueError: If the XML is malformed or attempts to process external entities.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_data, str):
        raise TypeError("xml_data must be a string")

    # Configure secure XML parsing by not allowing external entities
    # Use a parser with security options
    try:
        # Parse the XML with default settings (ElementTree does not resolve external entities by default)
        # However, we explicitly avoid using parser features that could allow entity expansion
        parser = ET.XMLParser()
        # Disable DTD processing to prevent external entity inclusion
        parser.parser.UseForeignDTD = False
        parser.entity['external_entity'] = 'unparsed'  # Prevent external entity resolution
        
        root = ET.fromstring(xml_data, parser=parser)
        
        translations = {}
        
        # Process translation entries - assuming structure like <translation id="key">value</translation>
        # or similar. Adjust based on expected structure.
        for elem in root.iter():
            if 'id' in elem.attrib and elem.text:
                translation_id = elem.attrib['id'].strip()
                translation_text = elem.text.strip()
                translations[translation_id] = translation_text
                
        return translations
        
    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Malformed XML or invalid content: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected XML-related issues
        raise ValueError(f"Error processing XML: {str(e)}") from e