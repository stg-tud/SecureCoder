import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from defusedxml.ElementTree import parse as safe_parse
from io import StringIO

def parse_xml_settings(xml_string):
    """
    Parse XML configuration data from a string, securely handling untrusted input.
    
    Args:
        xml_string: a string containing the XML to be parsed, representing configuration data
    
    Returns:
        The parsed configuration data in the form of a dictionary
    
    Raises:
        ValueError: if the provided XML is invalid or cannot be parsed
        TypeError: if the input is not a string
    
    Security Policy:
        - Prevents XXE attacks by disabling entity resolution and external entity loading
        - Uses defusedxml library to harden against known XML vulnerabilities
    """
    if not isinstance(xml_string, str):
        raise TypeError("xml_string must be a string")
    
    if not xml_string.strip():
        raise ValueError("xml_string cannot be empty")
    
    try:
        # Use defusedxml to prevent XXE attacks
        # This automatically disables DTD processing and external entities
        xml_file = StringIO(xml_string)
        safe_tree = safe_parse(xml_file)
        root = safe_tree.getroot()
        
        # Convert XML to dictionary
        def element_to_dict(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result["@attributes"] = element.attrib
            
            # Add text content if it exists and children don't exist
            has_text = element.text and element.text.strip()
            has_children = len(element) > 0
            
            if has_text and not has_children:
                return element.text.strip()
            elif has_text:
                result["@text"] = element.text.strip()
            
            # Add children
            for child in element:
                child_data = element_to_dict(child)
                if child.tag in result:
                    # If the tag already exists, convert to list
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        result = {root.tag: element_to_dict(root)}
        return result
        
    except (ET.ParseError, ExpatError, ValueError) as e:
        raise ValueError(f"Invalid XML: {str(e)}") from e
    except Exception as e:
        # Catch any other XML-related exceptions
        raise ValueError(f"Failed to parse XML: {str(e)}") from e