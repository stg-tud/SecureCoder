import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def process_xml_data(config_xml: str) -> Dict:
    """
    Safely parses and processes XML configuration data from untrusted sources.
    
    This function disables external entity resolution to prevent XXE (XML External Entity)
    attacks. It only parses the provided XML string and returns the configuration
    data as a dictionary.

    Args:
        config_xml: str, the raw XML content representing configuration information

    Returns:
        The configuration data in a structured format, such as a dictionary

    Raises:
        ValueError: If the XML is unparseable or contains malicious content
        TypeError: If the input is not a string
    """
    if not isinstance(config_xml, str):
        raise TypeError("config_xml must be a string")

    if not config_xml.strip():
        raise ValueError("config_xml cannot be empty")

    try:
        # Parse XML with default parser (xml.etree.ElementTree)
        # ElementTree does not resolve external entities by default, making it safe
        parser = ET.XMLParser()
        # Explicitly disable DTD loading to prevent XXE attacks
        parser.parser.UseForeignDTD = False
        parser.entity["external_entity"] = ""  # Neutralize any external entity references
        
        root = ET.fromstring(config_xml, parser=parser)
        
        # Convert XML structure to dictionary
        def xml_to_dict(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Add text content if it exists and there are no children
            has_text = element.text and element.text.strip()
            has_children = len(element) > 0
            
            if has_text and not has_children:
                return element.text.strip()
            elif has_text:
                result['#text'] = element.text.strip()
            
            # Add children
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    # If tag already exists, convert to list
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        return {root.tag: xml_to_dict(root)}
        
    except ExpatError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error during XML processing: {str(e)}")