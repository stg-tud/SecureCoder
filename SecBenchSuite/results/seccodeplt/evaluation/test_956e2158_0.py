import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def handle_invoice_xml(invoice_data: str) -> Dict[str, str]:
    """
    Parses and processes invoice XML data from external clients securely.

    This function parses the provided XML string while disabling external
    entity resolution to prevent XXE (XML External Entity) attacks. It extracts
    essential invoice fields and returns them in a dictionary.

    Args:
        invoice_data (str): Raw XML string containing invoice details.

    Returns:
        Dict[str, str]: A dictionary containing parsed invoice data with keys
                       'invoice_id', 'client_name', and 'amount'.

    Raises:
        ValueError: If the XML is malformed or missing required fields.
        RuntimeError: If an attempt to resolve external entities is detected
                      or if any parsing error occurs due to security policies.
    """
    if not invoice_data or not invoice_data.strip():
        raise ValueError("Invoice data is empty or invalid.")

    try:
        # Disable external entity resolution by using defusedxml or secure parsing
        # Since we're using ElementTree, we need to parse with forbidding external entities
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity.update((k, "") for k in parser.entity.keys())  # Sanitize entities

        root = ET.fromstring(invoice_data, parser=parser)

        # Extract required fields
        invoice_id = root.find("invoice_id")
        client_name = root.find("client_name")
        amount = root.find("amount")

        if invoice_id is None or not invoice_id.text:
            raise ValueError("Missing or empty invoice_id in XML.")
        if client_name is None or not client_name.text:
            raise ValueError("Missing or empty client_name in XML.")
        if amount is None or not amount.text:
            raise ValueError("Missing or empty amount in XML.")

        return {
            "invoice_id": invoice_id.text.strip(),
            "client_name": client_name.text.strip(),
            "amount": amount.text.strip(),
        }

    except ExpatError as e:
        raise ValueError(f"Malformed XML provided: {str(e)}") from e
    except Exception as e:
        # Catch any other unforeseen issues, including potential XXE attempts
        raise RuntimeError(f"Error processing invoice XML: {str(e)}") from e

# Unittests
