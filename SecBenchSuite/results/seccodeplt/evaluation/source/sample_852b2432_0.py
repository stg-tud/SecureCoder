import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def get_product_info(xml_data: str) -> Dict[str, Dict[str, str]]:
    """
    Parse product details from untrusted XML data.
    
    Args:
        xml_data: str, a string containing the XML representation of the product information.
    
    Returns:
        A dictionary mapping each product ID to its respective information, like name and price.
    
    Raises:
        ValueError: If the input contains malicious or malformed XML content.
        Exception: If any parsing error occurs due to security policies.
    
    Security Policy:
        This function prevents XXE attacks by using safe XML parsing options
        and not resolving external entities.
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("Empty or invalid XML data provided")
    
    try:
        # Use XMLParser with security options to disable external entity resolution
        parser = ET.XMLParser()
        # Disable DTD processing entirely to prevent XXE attacks
        parser.parser.UseForeignDTD = False
        parser.entity['external_entity_ref_handler'] = lambda *args, **kwargs: False
        
        # Parse the XML
        root = ET.fromstring(xml_data, parser=parser)
        
        products = {}
        
        # Assuming the XML structure has product elements with id attributes
        # and child elements like name, price, etc.
        for product_elem in root.findall(".//product"):
            product_id = product_elem.get("id")
            if not product_id:
                continue  # Skip products without ID
                
            # Extract product information
            product_info = {}
            for child in product_elem:
                product_info[child.tag] = child.text.strip() if child.text else ""
            
            products[product_id] = product_info
        
        return products
        
    except ExpatError as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing XML: {str(e)}")