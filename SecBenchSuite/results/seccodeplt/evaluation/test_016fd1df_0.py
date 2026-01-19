import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from defusedxml.ElementTree import parse as safe_parse
from io import StringIO

def process_config_xml(configuration_xml: str) -> dict:
    """
    Safely parse XML configuration data from untrusted sources.
    
    This function parses the provided XML string and returns a dictionary
    of configuration key-value pairs. It prevents XML External Entity (XXE)
    attacks by using secure parsing mechanisms that disable external entity
    resolution.

    Args:
        configuration_xml (str): A string containing the raw XML representing 
                               the configuration data.

    Returns:
        dict: A dictionary containing the parsed configuration key-value pairs.

    Raises:
        ValueError: If the XML data is improperly formatted or unparseable.
        TypeError: If the input is not a string.
    """
    if not isinstance(configuration_xml, str):
        raise TypeError("configuration_xml must be a string")

    if not configuration_xml.strip():
        raise ValueError("configuration_xml cannot be empty or whitespace only")

    try:
        # Use defusedxml to safely parse the XML string
        # defusedxml already disables external entity expansion by default
        config_dict = {}
        xml_source = StringIO(configuration_xml)
        safe_tree = safe_parse(xml_source)
        root = safe_tree.getroot()

        # Extract key-value pairs from the XML structure
        # Assuming a simple structure where child elements represent config entries
        # e.g., <config><key1>value1</key1><key2>value2</key2></config>
        for child in root:
            # Handle both element text and attributes if needed
            # For simplicity, we'll use element text as value
            config_dict[child.tag] = child.text.strip() if child.text else ""

        return config_dict

    except (ExpatError, ValueError, ET.ParseError) as e:
        raise ValueError(f"Failed to parse XML: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected exceptions from defusedxml
        raise ValueError(f"An error occurred while processing the XML: {str(e)}") from e

# Unittests
