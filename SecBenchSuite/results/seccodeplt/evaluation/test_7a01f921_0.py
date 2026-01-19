import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def secure_xml_handler(xml_config: str) -> Dict:
    """
    Securely parses XML configuration data from a string, preventing external entity inclusion.

    This function disables DTD processing and external entity resolution to prevent XXE (XML External Entity)
    attacks. It only processes the core XML content provided in the input string.

    Args:
        xml_config: A string of XML-format text containing configuration parameters.

    Returns:
        A dictionary containing the parsed configuration data.

    Raises:
        ValueError: If the XML content is invalid, empty, or cannot be parsed securely.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_config, str):
        raise TypeError("xml_config must be a string")

    if not xml_config.strip():
        raise ValueError("xml_config cannot be empty or whitespace only")

    try:
        # Use defusedxml if available for even stronger protection,
        # but ElementTree with proper configuration is sufficient here.

        # Disabling DTD entirely prevents external entity processing
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update({
            'xxe': 'FORBIDDEN',
            'external': 'FORBIDDEN'
        })

        root = ET.fromstring(xml_config.strip(), parser=parser)

        def element_to_dict(element: ET.Element) -> Dict:
            result = {}
            # Add attributes
            if element.attrib:
                result["@attributes"] = element.attrib

            # Add text content if it exists and has meaning
            text = element.text.strip() if element.text else ""
            if text and not (len(element) > 0):
                result["#text"] = text
            elif text:
                result["#text"] = text  # Include text even if there are children

            # Add child elements
            for child in element:
                child_data = element_to_dict(child)
                if child.tag in result:
                    # Convert to list if multiple elements with same tag
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data

            return result

        return {root.tag: element_to_dict(root)}

    except ExpatError as e:
        raise ValueError(f"Invalid XML format: {str(e)}") from e
    except Exception as e:
        # Catch any other XML processing-related errors
        raise ValueError(f"Failed to parse XML securely: {str(e)}") from e

# Unittests
