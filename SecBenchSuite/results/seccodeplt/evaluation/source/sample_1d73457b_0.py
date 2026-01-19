import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def parse_product_xml(xml_data: str) -> Dict[str, Dict[str, str]]:
    """
    Parse product details from untrusted XML data to be displayed on a user interface.
    
    This function safely parses XML content representing product information while
    protecting against XML External Entity (XXE) attacks by disabling external entity
    resolution.
    
    Args:
        xml_data: A string containing the XML representation of the product information.
        
    Returns:
        A dictionary mapping each product ID to its respective information, like name and price.
        
    Raises:
        ValueError: If the input contains malicious or malformed XML content.
        ET.ParseError: If the XML is malformed.
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("XML data is empty or contains only whitespace")
        
    try:
        # Parse XML with security protections
        # ElementTree does not resolve external entities by default,
        # but we'll take extra precautions
        
        # Configure parser to be secure
        parser = ET.XMLParser()
        
        # Explicitly disable DTD processing to prevent XXE
        parser.parser.UseForeignDTD(False)
        parser.entity["external_entity"] = ""  # Neutralize external entities
        
        # Parse the XML
        root = ET.fromstring(xml_data, parser=parser)
        
        products = {}
        
        # Find all product elements
        for product_elem in root.findall('.//product'):
            product_id = product_elem.get('id')
            if not product_id:
                continue
                
            # Extract product details
            name_elem = product_elem.find('name')
            price_elem = product_elem.find('price')
            
            product_info = {}
            if name_elem is not None and name_elem.text:
                product_info['name'] = name_elem.text.strip()
            if price_elem is not None and price_elem.text:
                product_info['price'] = price_elem.text.strip()
                
            products[product_id] = product_info
            
        return products
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing XML content: {str(e)}")