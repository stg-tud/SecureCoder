import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def parse_config_xml(xml_data: str) -> Dict[str, str]:
    """
    Safely parse XML configuration data from untrusted sources.

    - Prevents XXE (XML External Entity) attacks by disabling external entity resolution.
    - Returns a dictionary of configuration key-value pairs.
    - Raises an exception if the XML is malformed or contains disallowed constructs.

    Args:
        xml_data: A string containing the raw XML representing the configuration data.

    Returns:
        A dictionary containing the parsed configuration key-value pairs.

    Raises:
        ValueError: If the XML is malformed, unparseable, or contains external entities.
    """
    if not isinstance(xml_data, str):
        raise ValueError("xml_data must be a string")

    if not xml_data.strip():
        raise ValueError("xml_data cannot be empty")

    try:
        # Disable external entity resolution by using custom parser settings
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.parser.SetParamEntityParsing(0)  # Disable parameter entity parsing

        root = ET.fromstring(xml_data, parser=parser)

        config_dict = {}
        for elem in root.iter():
            # Only include elements with text content and no children
            if len(elem) == 0 and elem.text is not None:
                config_dict[elem.tag] = elem.text.strip()
            elif len(elem) > 0 and elem.text and elem.text.strip():
                # Include text even if there are children (e.g. mixed content)
                config_dict[elem.tag] = elem.text.strip()

        return config_dict

    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Failed to parse XML: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected XML processing issues
        raise ValueError(f"An error occurred while parsing XML: {str(e)}") from e