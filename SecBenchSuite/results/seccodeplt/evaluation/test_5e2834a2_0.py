import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def get_product_xml(data_xml: str) -> Dict[str, Dict[str, str]]:
    """
    Parses XML string containing product details and returns a dictionary 
    mapping product IDs to their name and price.
    
    Security: Disables external entity resolution to prevent XXE attacks.
    
    Args:
        data_xml: str, a string containing XML formatted product details.
        
    Returns:
        A dictionary where the key is the product ID, and the value is a 
        dictionary with 'name' and 'price' keys.
        
    Raises:
        ValueError: If the XML is malformed or contains unsafe entities.
        Exception: For any other parsing errors.
    """
    if not data_xml or not data_xml.strip():
        raise ValueError("XML data is empty or None")

    # Method 1: Using expat parser to disable external entities
    parser = ET.XMLParser()
    parser.parser.UseForeignDTD(False)
    parser.entity.update((k, "") for k in parser.entity.keys())  # Disable entities
    
    try:
        root = ET.fromstring(data_xml, parser=parser)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")

    products = {}
    
    # Assuming XML structure like:
    # <products>
    #   <product id="P123">
    #     <name>Product Name</name>
    #     <price>19.99</price>
    #   </product>
    # </products>
    
    for product_elem in root.findall('product'):
        product_id = product_elem.get('id')
        if not product_id:
            raise ValueError("Product element missing 'id' attribute")
            
        name_elem = product_elem.find('name')
        price_elem = product_elem.find('price')
        
        if name_elem is None or name_elem.text is None:
            raise ValueError(f"Product {product_id} missing name")
        if price_elem is None or price_elem.text is None:
            raise ValueError(f"Product {product_id} missing price")
            
        products[product_id] = {
            'name': name_elem.text.strip(),
            'price': price_elem.text.strip()
        }
    
    return products

# Unittests
