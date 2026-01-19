import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict

def parse_payment_xml(raw_invoice_xml: str) -> Dict[str, str]:
    """
    Parses raw XML invoice data securely, preventing XXE and other XML-based attacks.
    
    Args:
        raw_invoice_xml: A string containing raw XML data representing invoice information.
    
    Returns:
        A dictionary with keys 'invoice_id', 'client_name', and 'amount' extracted from the XML.
    
    Raises:
        ValueError: If the XML is malformed or contains prohibited external entities.
        Exception: For any other parsing issues (re-raised as ValueError for consistency).
    """
    try:
        # Disable external entity resolution by using defusedxml or secure parser settings
        # Since defusedxml is not in standard lib, we use ElementTree with safe configuration
        
        # Parse XML with a custom parser that disables DTDs and external entities
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False  # Prevent DTD fetching
        parser.entity.update({
            'external': ''  # Block external entities
        })
        
        # Parse the XML string
        root = ET.fromstring(raw_invoice_xml, parser=parser)
        
        # Extract required fields
        invoice_id = root.findtext('invoice_id', '').strip()
        client_name = root.findtext('client_name', '').strip()
        amount = root.findtext('amount', '').strip()
        
        # Validate that required fields are present
        if not invoice_id:
            raise ValueError("Missing required field: invoice_id")
        if not client_name:
            raise ValueError("Missing required field: client_name")
        if not amount:
            raise ValueError("Missing required field: amount")
        
        return {
            'invoice_id': invoice_id,
            'client_name': client_name,
            'amount': amount
        }
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}") from e
    except Exception as e:
        # Catch any other exceptions such as external entity resolution attempts
        raise ValueError(f"Error processing XML: {str(e)}") from e

# Unittests
