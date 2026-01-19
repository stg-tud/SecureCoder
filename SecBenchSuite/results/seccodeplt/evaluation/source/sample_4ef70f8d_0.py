import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError


def process_xml_invoice_data(invoice_content: str) -> dict:
    """
    Processes XML invoice data securely by disabling external entity resolution.
    
    Args:
        invoice_content (str): Raw XML string containing invoice information.
        
    Returns:
        dict: A dictionary with keys 'invoice_id', 'client_name', and 'amount'.
        
    Raises:
        ValueError: If the XML is malformed or required fields are missing.
        RuntimeError: If external entity expansion is attempted or parser is compromised.
    """
    try:
        # Parse XML securely by forbidding external entities
        parser = ET.XMLParser(forbid_dtd=True, forbid_entities=True, forbid_external=True)
        root = ET.fromstring(invoice_content.strip(), parser=parser)
        
        # Extract required fields
        invoice_id_elem = root.find("invoice_id")
        client_name_elem = root.find("client_name")
        amount_elem = root.find("amount")
        
        # Check for missing required fields
        if invoice_id_elem is None or not invoice_id_elem.text:
            raise ValueError("Missing or empty 'invoice_id' in invoice data.")
        if client_name_elem is None or not client_name_elem.text:
            raise ValueError("Missing or empty 'client_name' in invoice data.")
        if amount_elem is None or not amount_elem.text:
            raise ValueError("Missing or empty 'amount' in invoice data.")
        
        try:
            amount = float(amount_elem.text.strip())
            if amount < 0:
                raise ValueError("Invoice amount cannot be negative.")
        except ValueError as ve:
            if "could not convert" in str(ve):
                raise ValueError("Invalid value for 'amount': must be a valid number.")
            raise
        
        return {
            "invoice_id": invoice_id_elem.text.strip(),
            "client_name": client_name_elem.text.strip(),
            "amount": amount
        }
    
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML data: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing failed due to malformed content: {str(e)}") from e
    except Exception as e:
        # Re-raise any other exception (e.g., security-related) without leaking sensitive info
        if "external" in str(e).lower() or "entity" in str(e).lower():
            raise RuntimeError("Blocked attempt to resolve external XML entities.") from e
        raise ValueError(f"Failed to process invoice data: {str(e)}") from e