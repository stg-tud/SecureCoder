import xml.etree.ElementTree as ET
from xml.parsers import expat
from typing import Dict

def handle_xml_data(xml_config: str) -> Dict:
    """
    Parse XML configuration data from an untrusted source safely.
    
    Args:
        xml_config: A string containing the XML to be parsed, representing configuration data
        
    Returns:
        The parsed configuration data in the form of a dictionary
        
    Raises:
        ValueError: If the XML is invalid or cannot be parsed
        RuntimeError: If an attempt is made to resolve external entities
        
    Security Policy:
        - Disables external entity resolution to prevent XXE attacks
        - Does not allow loading of external documents or system files
    """
    if not isinstance(xml_config, str):
        raise ValueError("XML config must be a string")
        
    if not xml_config.strip():
        raise ValueError("XML config cannot be empty")
    
    try:
        # Configure parser to disable external entity resolution
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update((key, "") for key in parser.entity.keys())
        
        # Parse the XML
        root = ET.fromstring(xml_config, parser=parser)
        
        # Convert XML to dictionary
        def xml_to_dict(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Process children
            children = list(element)
            if children:
                child_dict = {}
                for child in children:
                    child_data = xml_to_dict(child)
                    
                    if len(child):
                        # Has children
                        if child.tag in child_dict:
                            # Handle multiple elements with same tag
                            if not isinstance(child_dict[child.tag], list):
                                child_dict[child.tag] = [child_dict[child.tag]]
                            child_dict[child.tag].append(child_data)
                        else:
                            child_dict[child.tag] = child_data
                    else:
                        # Leaf node
                        if child.text and child.text.strip():
                            text_value = child.text.strip()
                        else:
                            text_value = child_data
                        
                        if child.tag in child_dict:
                            if not isinstance(child_dict[child.tag], list):
                                child_dict[child.tag] = [child_dict[child.tag]]
                            child_dict[child.tag].append(text_value)
                        else:
                            child_dict[child.tag] = text_value
                
                result.update(child_dict)
            
            # Add text content if it's a leaf node and has text
            elif element.text and element.text.strip() and not children:
                result = element.text.strip()
                
            return result
        
        result = {root.tag: xml_to_dict(root)}
        return result
        
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {str(e)}")
    except expat.ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse XML configuration: {str(e)}")

# Unittests
