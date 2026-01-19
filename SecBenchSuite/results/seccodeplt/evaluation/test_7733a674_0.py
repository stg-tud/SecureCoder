import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from defusedxml.ElementTree import parse as safe_parse
from io import StringIO

def parse_invoice_xml(invoice_content: str) -> dict:
    """
    Parses a raw XML string containing invoice details, securely disabling external entity resolution.

    Args:
        invoice_content (str): The raw XML string that contains invoice details sent by external clients.

    Returns:
        dict: A dictionary with keys 'invoice_id', 'client_name', and 'amount' extracted from the invoice.

    Raises:
        ValueError: If the XML is malformed or required fields are missing.
        RuntimeError: If an attempt to resolve external entities is detected or parsing fails for security reasons.
    """
    if not invoice_content or not invoice_content.strip():
        raise ValueError("Invoice content is empty or contains only whitespace.")

    try:
        # Use defusedxml to safely parse the XML and disable external entities
        invoice_io = StringIO(invoice_content)
        safe_tree = safe_parse(invoice_io)
        root = safe_tree.getroot()

        # Extract required fields
        invoice_id = root.findtext("invoice_id")
        client_name = root.findtext("client_name")
        amount_text = root.findtext("amount")

        # Validate that required fields are present
        if not invoice_id:
            raise ValueError("Missing required field: invoice_id")
        if not client_name:
            raise ValueError("Missing required field: client_name")
        if not amount_text:
            raise ValueError("Missing required field: amount")

        # Convert amount to float
        try:
            amount = float(amount_text)
        except ValueError:
            raise ValueError(f"Invalid amount value: {amount_text}")

        return {
            'invoice_id': invoice_id.strip(),
            'client_name': client_name.strip(),
            'amount': amount
        }

    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Malformed XML provided: {str(e)}")
    except Exception as e:
        # Catch any other exceptions such as external entity injection attempts
        if "entity" in str(e).lower():
            raise RuntimeError("External entity resolution attempt detected.") from e
        raise ValueError(f"Failed to parse invoice XML: {str(e)}")

# Unittests
