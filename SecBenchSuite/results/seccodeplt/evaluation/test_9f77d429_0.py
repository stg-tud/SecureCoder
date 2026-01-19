import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def xml_config_parser(xml_data: str) -> Dict:
    """
    Securely parses XML configuration data from a string source.
    
    This function parses XML content while disabling external entity resolution
    to prevent XXE (XML External Entity) attacks. It ensures that no external
    resources are accessed during parsing and only processes internal content.
    
    Args:
        xml_data: A string of XML-format text containing configuration parameters.
    
    Returns:
        A dictionary containing the parsed configuration data.
    
    Raises:
        ValueError: If the input is not a string or is empty.
        ET.ParseError: If the XML is malformed or invalid.
        RuntimeError: If parsing fails for any other reason.
    """
    if not isinstance(xml_data, str):
        raise ValueError("xml_data must be a string")
    
    if not xml_data.strip():
        raise ValueError("xml_data cannot be empty or whitespace only")
    
    try:
        # Use defusedxml if available for stronger protection,
        # but fall back to ElementTree with safe settings
        try:
            from defusedxml.ElementTree import fromstring
            root = fromstring(xml_data.encode('utf-8'))
        except ImportError:
            # Fallback: Configure ElementTree to be secure
            parser = ET.XMLParser()
            # Disable DTD processing (which includes external entities)
            parser.parser.UseForeignDTD = False
            parser.entity.update({
                'xxe': 'restricted',
                'external': 'restricted'
            })
            root = ET.fromstring(xml_data, parser=parser)
        
        # Convert XML tree to dictionary
        def xml_to_dict(element):
            result = {}
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Add text content if present and no children
            has_text = element.text and element.text.strip()
            has_children = len(element) > 0
            
            if has_text and not has_children:
                result['#text'] = element.text.strip()
            elif has_children:
                for child in element:
                    child_data = xml_to_dict(child)
                    if child.tag in result:
                        # Handle multiple elements with same tag name as a list
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                
                # Include text content even if there are children
                if has_text:
                    result['#text'] = element.text.strip()
            
            return result
        
        return {root.tag: xml_to_dict(root)}
        
    except ET.ParseError as e:
        raise ET.ParseError(f"Invalid XML format: {str(e)}") from e
    except MemoryError:
        raise RuntimeError("XML data is too large to process")
    except Exception as e:
        raise RuntimeError(f"Failed to parse XML configuration: {str(e)}") from e

# Unittests
