import xml.etree.ElementTree as ET
from xml.parsers import expat
from typing import Dict

def parse_xml_config(xml_data: str) -> Dict:
    """
    Parse XML configuration data from a string and return it as a dictionary.
    
    Args:
        xml_data: A string containing the XML to be parsed, representing configuration data.
        
    Returns:
        The parsed configuration data in the form of a dictionary.
        
    Raises:
        ValueError: If the XML is invalid or cannot be parsed.
        Exception: If any parsing error occurs.
        
    Security Policy:
        - Disables external entity resolution to prevent XXE attacks.
        - Does not allow loading of external documents or system files.
    """
    if not isinstance(xml_data, str):
        raise ValueError("xml_data must be a string")
    
    if not xml_data.strip():
        raise ValueError("xml_data cannot be empty")

    try:
        # Configure parser to disable external entity resolution
        parser = ET.XMLParser()
        
        # Disable DTD loading entirely to prevent XXE attacks
        parser.parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
        parser.parser.UseForeignDTD(False)
        
        # Parse the XML
        root = ET.fromstring(xml_data, parser=parser)
        
        # Convert XML tree to dictionary
        def element_to_dict(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Add text content if it exists and there are no children
            has_children = len(element) > 0
            if element.text and element.text.strip() and not has_children:
                result['#text'] = element.text.strip()
            elif element.text and element.text.strip():
                result['#text'] = element.text.strip()
            
            # Add children
            for child in element:
                child_data = element_to_dict(child)
                if child.tag in result:
                    # If tag already exists, convert to list
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        result = {root.tag: element_to_dict(root)}
        return result
        
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {str(e)}")
    except expat.ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        # Catch any other XML-related exceptions
        raise ValueError(f"Failed to parse XML: {str(e)}")