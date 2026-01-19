import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
import logging

def parse_translation_content(xml_data: str) -> dict:
    """
    Securely parse XML data containing translation mappings.

    Args:
        xml_data: str, representing XML input which holds translation mappings for various text identifiers.

    Returns:
        A dictionary where each key corresponds to a phrase ID, and the value represents the corresponding translated text.

    Raises:
        ValueError: If the XML content is invalid, malformed, or contains external entity references.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_data, str):
        raise TypeError("xml_data must be a string")

    if not xml_data.strip():
        raise ValueError("xml_data cannot be empty or whitespace only")

    try:
        # Use defusedxml to safely parse the XML string and prevent external entity resolution
        root = fromstring(xml_data)
        
        translations = {}
        for element in root.findall(".//translation") + root.findall(".//entry") + root.findall("."):
            # Look for common patterns: elements with id and text/content
            phrase_id = element.get("id") or element.get("key")
            if phrase_id:
                # Get text content, stripping whitespace
                translated_text = element.text
                if translated_text is not None:
                    translated_text = translated_text.strip()
                else:
                    # Handle case where translation might be in a child or attribute
                    translated_text = element.get("value") or element.get("text", "").strip()
                
                translations[phrase_id] = translated_text
        
        # Alternative structure: <translations><item id="...">text</item></translations>
        if not translations:
            for item in root:
                phrase_id = item.get("id") or item.get("key")
                if phrase_id and item.text:
                    translations[phrase_id] = item.text.strip()
        
        return translations

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}") from e
    except Exception as e:
        # Catch any other exceptions (e.g., from defusedxml for suspected attacks)
        raise ValueError(f"Failed to parse XML securely: {str(e)}") from e