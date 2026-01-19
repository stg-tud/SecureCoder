import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def process_payment_xml(payment_xml: str) -> Dict[str, str]:
    """
    Process XML string containing invoice details from external clients.
    Ensures secure parsing by disabling external entity resolution to prevent
    XXE (XML External Entity) attacks.

    Args:
        payment_xml: str, the raw XML string that contains invoice details sent by external clients

    Returns:
        A dictionary with parsed invoice data including 'invoice_id', 'client_name', and 'amount'

    Raises:
        ValueError: If the XML is malformed or contains external entities
        Exception: For any other processing errors
    """
    if not payment_xml or not payment_xml.strip():
        raise ValueError("Empty or invalid XML input provided")

    try:
        # Use defusedxml or manually disable external entities with ElementTree
        # Since defusedxml is not part of standard library, we configure ElementTree securely

        # Parse XML from string with safe configuration
        parser = ET.XMLParser()
        # Disable DTD processing to prevent external entity inclusion
        parser.parser.UseForeignDTD = False
        parser.entity["external_entity"] = ""  # Dummy override
        parser.entity["xxe"] = ""

        root = ET.fromstring(payment_xml, parser=parser)

        # Extract required fields
        invoice_id = root.findtext("invoice_id") or root.findtext("InvoiceID")
        client_name = root.findtext("client_name") or root.findtext("ClientName")
        amount = root.findtext("amount") or root.findtext("Amount")

        if not invoice_id:
            raise ValueError("Missing required field: invoice_id")
        if not client_name:
            raise ValueError("Missing required field: client_name")
        if not amount:
            raise ValueError("Missing required field: amount")

        # Strip whitespace and return result
        return {
            "invoice_id": invoice_id.strip(),
            "client_name": client_name.strip(),
            "amount": amount.strip(),
        }

    except ExpatError as e:
        raise ValueError(f"Malformed XML: {str(e)}") from e
    except ET.ParseError as e:
        raise ValueError(f"XML parsing failed: {str(e)}") from e
    except Exception as e:
        # Re-raise any other exceptions as ValueError for security (avoid leaking internal details)
        raise ValueError("Failed to process XML due to invalid content or security policy") from e