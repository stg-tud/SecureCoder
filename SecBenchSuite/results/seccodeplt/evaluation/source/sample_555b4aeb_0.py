import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from defusedxml.ElementTree import parse as safe_parse
from io import StringIO

def load_product_xml(xml_content: str) -> dict:
    """
    Parses XML content containing product details and returns a dictionary
    with product ID as key and name and price as values.
    
    This function is secure against XXE (XML External Entity) attacks by
    using defusedxml to disable external entity resolution.
    
    Args:
        xml_content: str, the XML data containing product details
        
    Returns:
        dict: A dictionary where the product ID is the key, and the value is
              a dict containing 'name' and 'price' of the product.
              
    Raises:
        ValueError: If the XML is invalid or contains unsafe constructs.
        TypeError: If xml_content is not a string.
    """
    if not isinstance(xml_content, str):
        raise TypeError("xml_content must be a string")

    if not xml_content.strip():
        raise ValueError("xml_content cannot be empty")

    try:
        # Use defusedxml to prevent XXE attacks
        # This disables external entities and DTD loading by default
        parser = safe_parse(StringIO(xml_content))
        root = parser.getroot()
    except (ET.ParseError, ExpatError, ValueError) as e:
        raise ValueError(f"Invalid XML data: {str(e)}")
    except Exception as e:
        # Catch any other potential issues from defusedxml
        if "external entity" in str(e).lower() or "DTD" in str(e).lower():
            raise ValueError("Unsafe XML entity detected")
        raise ValueError(f"Failed to parse XML: {str(e)}")

    products = {}
    
    # Expected structure: <products><product id="...">...</product></products>
    # or <product id="...">...</product>
    root_tag = root
    if root.tag.lower() == 'products':
        product_elements = root.findall('product')
    else:
        product_elements = [root] if root.tag.lower() == 'product' else []

    for elem in product_elements:
        product_id = elem.get('id')
        if not product_id:
            raise ValueError("Product element missing 'id' attribute")
            
        # Extract name
        name_elem = elem.find('name')
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ''
        if not name:
            raise ValueError(f"Product with id '{product_id}' is missing name")

        # Extract price
        price_elem = elem.find('price')
        if price_elem is None or price_elem.text is None:
            raise ValueError(f"Product with id '{product_id}' is missing price")
        
        try:
            price = float(price_elem.text.strip())
            if price < 0:
                raise ValueError(f"Price cannot be negative")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid price format for product '{product_id}': {str(e)}")

        products[product_id] = {
            'name': name,
            'price': price
        }

    return products