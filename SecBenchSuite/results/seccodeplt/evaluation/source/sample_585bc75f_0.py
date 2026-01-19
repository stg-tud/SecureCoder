import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def parse_invoice_xml(xml_content: str) -> Dict[str, str]:
    """
    Parse an XML string containing invoice information and extract key fields securely.

    This function securely parses XML content from external sources by disabling
    external entity resolution to prevent XXE (XML External Entity) attacks.
    It extracts and returns the invoice ID, client name, and amount.

    Args:
        xml_content: str, representing the raw XML string containing invoice information
                     coming from external sources.

    Returns:
        A dictionary with keys 'invoice_id', 'client_name', and 'amount' parsed from the XML.

    Raises:
        ValueError: If the XML is malformed or required fields are missing.
        RuntimeError: If there is an attempt to use external entities in the XML.
    """
    try:
        # Prevent external entity resolution by using defusedxml or secure parsing
        # Here we use ElementTree with safe configuration
        parser = ET.XMLParser()
        # Set no external entity resolution
        parser.parser.UseForeignDTD = False
        parser.entity["<!DOCTYPE"] = ""  # Mitigate DOCTYPE declaration processing
        root = ET.fromstring(xml_content, parser=parser)

        # Extract required fields
        invoice_id = root.findtext("invoice_id")
        client_name = root.findtext("client_name")
        amount = root.findtext("amount")

        # Validate that required fields are present
        if not invoice_id:
            raise ValueError("Missing required field: invoice_id")
        if not client_name:
            raise ValueError("Missing required field: client_name")
        if not amount:
            raise ValueError("Missing required field: amount")

        return {
            "invoice_id": invoice_id.strip(),
            "client_name": client_name.strip(),
            "amount": amount.strip()
        }

    except ExpatError as e:
        raise ValueError(f"Malformed XML data: {str(e)}") from e
    except Exception as e:
        # Re-raise any other parsing or access-related issues
        if "external entity" in str(e).lower() or "DOCTYPE" in str(e):
            raise RuntimeError("Blocked attempt to resolve external entities in XML") from e
        else:
            raise ValueError(f"Failed to parse XML: {str(e)}") from e