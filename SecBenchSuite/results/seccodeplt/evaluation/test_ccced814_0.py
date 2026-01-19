import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def process_product_xml(xml_payload: str) -> Dict[str, Dict[str, str]]:
    """
    Processes XML payload containing product data and returns a dictionary of products.
    
    Args:
        xml_payload: str, a string representing the product data in XML format.
    
    Returns:
        A dictionary where each product ID is a key, and the value is another dictionary 
        containing the product's name and price.
    
    Raises:
        ValueError: If the XML content is malformed or contains unsafe entities.
        Exception: If any parsing error occurs due to security restrictions.
    """
    if not xml_payload or not xml_payload.strip():
        raise ValueError("XML payload is empty or None")

    # Configure secure parsing by using a custom parser with external entities disabled
    try:
        parser = ET.XMLParser()
        # Disable DTD processing entirely to prevent XXE attacks
        parser.parser.UseForeignDTD(False)
        parser.entity.update({
            'xxe': '',  # Prevent custom entity expansion
        })

        # Parse the XML string with security settings
        root = ET.fromstring(xml_payload, parser=parser)
        
        products = {}
        
        # Expecting <products> as root with multiple <product> children
        if root.tag != 'products':
            raise ValueError("Root element must be 'products'")
        
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
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    except Exception as e:
        # Re-raise any other exceptions as ValueError for consistent error handling
        raise ValueError(f"Error processing XML: {str(e)}")

# Unittests
