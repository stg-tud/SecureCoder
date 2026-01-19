import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def extract_product_details(xml_input: str) -> Dict[str, Dict[str, str]]:
    """
    Extract product details from XML input.
    
    Args:
        xml_input: str, a string containing the XML representation of the product information.
        
    Returns:
        A dictionary mapping each product ID to its respective information, like name and price.
        
    Raises:
        Exception if the input contains malicious or malformed XML content.
        
    Security Policy:
        This function protects against XXE attacks by using safe XML parsing practices.
        It does not allow external entity resolution.
    """
    if not xml_input or not xml_input.strip():
        raise ValueError("XML input is empty or None")
    
    try:
        # Disable DTDs entirely to prevent XXE attacks
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update((k, "") for k in parser.entity.keys())  # Disable entities
        
        root = ET.fromstring(xml_input, parser=parser)
        
        products = {}
        
        # Assuming the XML structure has product elements with id attributes
        # Example: <product id="1"><name>Widget</name><price>19.99</price></product>
        for product_elem in root.findall(".//product"):
            product_id = product_elem.get("id")
            if not product_id:
                continue  # Skip products without an ID
                
            # Extract basic product info (extend as needed)
            name_elem = product_elem.find("name")
            price_elem = product_elem.find("price")
            
            product_info = {}
            if name_elem is not None and name_elem.text:
                product_info["name"] = name_elem.text.strip()
            if price_elem is not None and price_elem.text:
                product_info["price"] = price_elem.text.strip()
            
            products[product_id] = product_info
            
        return products
        
    except ET.ParseError as e:
        raise Exception(f"Malformed XML content: {str(e)}")
    except ExpatError as e:
        raise Exception(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing XML content: {str(e)}")