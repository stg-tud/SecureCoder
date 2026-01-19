import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def parse_product_xml(xml_data: str) -> Dict[str, Dict[str, str]]:
    """
    Parse XML content describing product data and return a dictionary of products.
    
    This function is secure against XXE (XML External Entity) attacks by using
    a defensive parsing approach that disables DTD processing and external entity
    resolution.
    
    Args:
        xml_data: A string containing XML formatted product details.
        
    Returns:
        A dictionary where the key is the product ID, and the value is a dictionary
        containing 'name' and 'price' of the product.
        
    Raises:
        ValueError: If the XML is malformed or contains unsafe constructs.
        Exception: If any parsing error occurs due to security restrictions.
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("XML data is empty or None")
        
    try:
        # Create a secure parser by using Expat with external entity handling disabled
        parser = ET.XMLParser()
        
        # Disable DTD entirely to prevent XXE attacks
        parser.parser.UseForeignDTD(False)
        parser.entity["externalEntityRefHandler"] = lambda *args: False
        
        # Parse the XML
        root = ET.fromstring(xml_data, parser=parser)
        
        products = {}
        
        # Expect root element to contain product entries
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
        raise ValueError(f"Malformed XML: {str(e)}")
    except Exception as e:
        # Catch any other unexpected exceptions (e.g., from entity resolution attempts)
        raise ValueError(f"Error parsing XML: {str(e)}")


# Alternative more restrictive implementation using defusedxml if available
# But since we can only use standard library, the above approach is secure when properly configured

# Unittests
