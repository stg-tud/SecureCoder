import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def parse_invoice_data(raw_xml: str) -> Dict[str, str]:
    """
    Parses invoice data from raw XML string securely.

    Args:
        raw_xml: A string containing raw XML data representing invoice information.

    Returns:
        A dictionary with keys 'invoice_id', 'client_name', and 'amount' extracted from the XML.

    Raises:
        ValueError: If the XML is malformed or contains external entities.
        Exception: If any parsing error occurs due to security configurations.
    """
    if not raw_xml or not raw_xml.strip():
        raise ValueError("Empty or invalid XML input")

    try:
        # Disable resolution of external entities by using custom parser settings
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update((key, "") for key in parser.entity.keys())  # Neutralize entities

        root = ET.fromstring(raw_xml, parser=parser)

        # Extract required fields
        invoice_id = root.findtext("invoice_id")
        client_name = root.findtext("client_name")
        amount = root.findtext("amount")

        if invoice_id is None:
            raise ValueError("Missing required field: invoice_id")
        if client_name is None:
            raise ValueError("Missing required field: client_name")
        if amount is None:
            raise ValueError("Missing required field: amount")

        return {
            "invoice_id": invoice_id.strip(),
            "client_name": client_name.strip(),
            "amount": amount.strip()
        }

    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}") from e
    except Exception as e:
        # Re-raise any other unexpected exception (e.g., from security violations)
        raise ValueError(f"Error parsing invoice data: {str(e)}") from e

# Unittests
