import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def fetch_product_xml(xml_data: str) -> Dict[str, Dict[str, str]]:
    """
    Parses XML string containing product data and returns a dictionary of products.
    
    Args:
        xml_data: str, a string representing the product data in XML format.
    
    Returns:
        A dictionary where each product ID is a key, and value is another dictionary 
        holding the product's name and price.
    
    Raises:
        ValueError: If the XML content is malformed or contains unsafe entities.
        Exception: If any parsing error occurs due to disabled external entities.
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("XML data is empty or None")
    
    # Configure secure parsing to prevent XXE
    parser = ET.XMLParser()
    # Disable DTD processing entirely to prevent XXE attacks
    parser.parser.UseForeignDTD = False
    parser.entity.update({
        'ent': '',  # Prevent entity expansion
    })
    
    try:
        # Parse the XML with secure parser
        root = ET.fromstring(xml_data.strip(), parser=parser)
        
        products = {}
        
        # Validate root element
        if root.tag != 'products':
            raise ValueError("Root element must be 'products'")
        
        # Process each product
        for product_elem in root.findall('product'):
            product_id = product_elem.get('id')
            if not product_id:
                raise ValueError("Product element must have an 'id' attribute")
            
            # Extract name
            name_elem = product_elem.find('name')
            if name_elem is None or not name_elem.text:
                raise ValueError(f"Product {product_id} must have a name")
            name = name_elem.text.strip()
            
            # Extract price
            price_elem = product_elem.find('price')
            if price_elem is None or not price_elem.text:
                raise ValueError(f"Product {product_id} must have a price")
            price = price_elem.text.strip()
            
            products[product_id] = {
                'name': name,
                'price': price
            }
        
        return products
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    except Exception as e:
        # Re-raise any other exceptions as ValueError for consistency
        raise ValueError(f"Error processing XML: {str(e)}")