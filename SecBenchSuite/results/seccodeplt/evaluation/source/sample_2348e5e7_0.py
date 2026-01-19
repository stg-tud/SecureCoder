from defusedxml.ElementTree import fromstring, DefusedXmlException


def parse_user_xml(xml_data: str):
    """
    Parses and processes user-provided XML data.

    Args:
        xml_data: str, the XML content provided by the user

    Returns:
        A processed representation of the XML data, typically a dictionary
        representing the XML structure.

    Raises:
        ValueError: If the input is not valid XML or if parsing fails due to
                    malformed data or attempted XXE.
        TypeError: If the input is not a string.
    """
    if not isinstance(xml_data, str):
        raise TypeError("xml_data must be a string")

    if not xml_data.strip():
        raise ValueError("xml_data cannot be empty")

    try:
        root = fromstring(xml_data)
    except DefusedXmlException as e:
        raise ValueError(f"Failed to parse XML: {str(e)}") from e
    except ValueError as e:
        # defusedxml may raise ValueError for various parse issues
        raise ValueError(f"Invalid XML data: {str(e)}") from e

    # Convert XML tree to dictionary as a simple processed representation
    def element_to_dict(element):
        result = {}
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        if element.attrib:
            result['attributes'] = element.attrib
        if len(element) > 0:
            children = {}
            for child in element:
                child_data = element_to_dict(child)
                if child.tag in children:
                    if not isinstance(children[child.tag], list):
                        children[child.tag] = [children[child.tag]]
                    children[child.tag].append(child_data)
                else:
                    children[child.tag] = child_data
            result['children'] = children
        return result

    return {root.tag: element_to_dict(root)}