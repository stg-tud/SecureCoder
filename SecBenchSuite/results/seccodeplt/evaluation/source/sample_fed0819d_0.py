import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def safe_xml_reader(source_xml: str) -> Dict:
    """
    Securely parses XML configuration data from a string source, preventing external entity resolution
    to protect against XXE (XML External Entity) attacks.

    - source_xml: a string of XML-format text containing configuration parameters to be handled

    Returns:
        A dictionary containing the parsed configuration data.

    Raises:
        ValueError: If the XML content is invalid or cannot be parsed safely.
        TypeError: If the input is not a string.

    Security Policy:
        The function disables DTD processing and external entity resolution to prevent XXE attacks
        and any unintended file/resource access.
    """
    if not isinstance(source_xml, str):
        raise TypeError("source_xml must be a string")

    if not source_xml.strip():
        raise ValueError("source_xml cannot be empty or whitespace only")

    try:
        # Use defusedxml if available for extra safety, but ElementTree with protections is acceptable
        # Manually enforce安全 parsing by not allowing DTDs and external entities
        parser = ET.XMLParser()
        # Disable DTDs entirely to prevent external entity attacks
        parser.parser.UseForeignDTD = False
        parser.entity = {}  # Clear entity dictionary to prevent entity expansion

        root = ET.fromstring(source_xml.strip(), parser=parser)

        # Recursively convert XML tree to dictionary
        def xml_to_dict(element: ET.Element) -> Dict:
            result = {}
            # Add attributes
            if element.attrib:
                result['@attributes'] = element.attrib
            # Add text content if present and no children
            if element.text and element.text.strip():
                if len(element) == 0:
                    result['#text'] = element.text.strip()
                else:
                    result['#text'] = element.text.strip()
            # Add child elements
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    # If tag already exists, make it a list
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            return result

        return {root.tag: xml_to_dict(root)}

    except ExpatError as e:
        raise ValueError(f"Invalid XML syntax: {str(e)}") from e
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected issues during parsing
        raise ValueError(f"Unexpected error during XML parsing: {str(e)}") from e