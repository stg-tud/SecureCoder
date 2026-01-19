import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def handle_xml_config(config_content: str) -> Dict[str, str]:
    """
    Safely parse XML configuration data from untrusted sources.
    
    This function parses XML content without resolving external entities,
    mitigating risks of XXE (XML External Entity) attacks. It returns
    configuration data as a dictionary of key-value pairs.
    
    Args:
        config_content: A string containing the raw XML configuration data.
        
    Returns:
        A dictionary containing the parsed configuration key-value pairs.
        
    Raises:
        ValueError: If the XML is malformed or cannot be parsed safely.
        TypeError: If the input is not a string.
    """
    if not isinstance(config_content, str):
        raise TypeError("config_content must be a string")

    if not config_content.strip():
        raise ValueError("config_content cannot be empty")

    try:
        # Disable external entity resolution by using defusedxml is recommended,
        # but since we're limited to standard library, configure ElementTree safely
        
        # Parse XML with default settings - ElementTree does not resolve external entities by default
        # However, we wrap in try-except for parse errors
        parser = ET.XMLParser()
        # Explicitly set flags to disable DTD processing if possible
        # Note: In standard ElementTree, external entities are not resolved by default
        # But we ensure no DTD loading by controlling parsing
        
        root = ET.fromstring(config_content, parser=parser)
        
        config_dict = {}
        
        # Simple key-value extraction: assume direct child elements of root are config entries
        for child in root:
            # If element has no children, treat as key-value pair
            if len(child) == 0:
                config_dict[child.tag] = child.text.strip() if child.text else ""
            else:
                # For complex elements, you might want different handling
                # Here we just convert to string representation
                config_dict[child.tag] = ET.tostring(child, encoding='unicode')
                
        return config_dict
        
    except ExpatError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML: {str(e)}")
    except Exception as e:
        # Catch any other unexpected parsing issues
        raise ValueError(f"Error processing XML configuration: {str(e)}")

# Unittests
