import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def fetch_product_xml(content_xml: str) -> Dict[str, Dict[str, str]]:
    """
    Parses XML content containing product details and returns a dictionary of products.
    
    Args:
        content_xml: A string containing XML formatted product details.
        
    Returns:
        A dictionary where the key is the product ID, and the value is a dictionary
        containing the product 'name' and 'price'.
        
    Raises:
        ValueError: If the XML is malformed or contains unsafe entities.
        Exception: If any parsing error occurs due to security restrictions.
    """
    if not content_xml or not content_xml.strip():
        raise ValueError("XML content is empty or None")

    try:
        # Use defusedxml if available for extra safety, but using ElementTree with security
        # precautions as defusedxml is not in standard library
        parser = ET.XMLParser()
        # Disable DTDs entirely to prevent XXE attacks
        parser.parser.UseForeignDTD = False
        parser.entity["externalEntityRefHandler"] = lambda *args, **kwargs: False
        parser.entity["parameterEntityHandler"] = lambda *args, **kwargs: False
        parser.entity["doctypeHandler"] = lambda *args, **kwargs: False

        root = ET.fromstring(content_xml, parser=parser)

    except (ExpatError, ET.ParseError) as e:
        raise ValueError(f"Malformed XML or unsafe content detected: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")

    products = {}

    # Assuming XML structure like:
    # <products>
    #   <product id="1">
    #     <name>Product Name</name>
    #     <price>19.99</price>
    #   </product>
    # </products>
    for product_elem in root.findall("product"):
        product_id = product_elem.get("id")
        if not product_id:
            continue  # Skip products without an ID

        name_elem = product_elem.find("name")
        price_elem = product_elem.find("price")

        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
        price = price_elem.text.strip() if price_elem is not None and price_elem.text else ""

        products[product_id] = {
            "name": name,
            "price": price
        }

    return products

# Unittests
