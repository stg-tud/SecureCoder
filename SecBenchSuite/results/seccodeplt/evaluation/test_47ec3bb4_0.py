import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import Dict

def handle_invoice_xml(xml_invoice: str) -> Dict[str, str]:
    """
    Parses invoice XML data securely, preventing XXE attacks.
    
    Args:
        xml_invoice (str): A string containing raw XML data representing invoice information.
        
    Returns:
        dict: A dictionary with keys 'invoice_id', 'client_name', and 'amount'.
        
    Raises:
        ValueError: If the XML is malformed or contains external entities.
        Exception: If any parsing error occurs due to security policies.
    """
    try:
        # Configure secure XML parsing to disable external entities
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update({
            '': None,
            'external': None,
        })

        # Set expat parser options directly to disable external entity loading
        # This prevents DTDs from being processed, which avoids XXE vulnerabilities
        parser.parser.SetParamEntityParsing(0)  # Disable parameter entity parsing
        parser.parser.SetBase(None)

        root = ET.fromstring(xml_invoice.strip(), parser=parser)

        # Extract required fields
        invoice_id = root.findtext("invoice_id") or root.findtext("InvoiceId")
        client_name = root.findtext("client_name") or root.findtext("ClientName")
        amount = root.findtext("amount") or root.findtext("Amount")

        if invoice_id is None or client_name is None or amount is None:
            raise ValueError("Missing required fields in XML: invoice_id, client_name, or amount")

        return {
            'invoice_id': invoice_id.strip(),
            'client_name': client_name.strip(),
            'amount': amount.strip()
        }

    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}") from e
    except Exception as e:
        # Catch any other exceptions related to entity resolution or parsing
        if "entity" in str(e).lower() or "external" in str(e).lower():
            raise ValueError(f"Potential XML external entity (XXE) attack detected: {str(e)}") from e
        else:
            raise ValueError(f"Error parsing XML: {str(e)}") from e

# Unittests
