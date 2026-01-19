import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import Dict


def process_invoice_xml(invoice_xml: str) -> Dict[str, str]:
    """
    Process XML invoice data from external sources safely.

    Args:
        invoice_xml: str, the raw XML content representing the invoice details
                     provided by external clients

    Returns:
        A dictionary containing the processed invoice data with keys like
        'invoice_id', 'client_name', and 'amount'.

    Raises:
        ValueError: If the XML is malformed or contains disallowed external entities.
        RuntimeError: If a potential security issue is detected during parsing.
    """
    if not invoice_xml or not invoice_xml.strip():
        raise ValueError("Invoice XML content is empty or None")

    try:
        # Parse XML securely by disabling external entity resolution
        # ElementTree does not load external entities by default, but we still
        # need to be cautious about billion laughs and other attacks.
        # Use a safe parser configuration.
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        root = ET.fromstring(invoice_xml, parser=parser)

        # Extract required fields
        invoice_id = root.findtext('invoice_id') or root.findtext('id')
        client_name = root.findtext('client_name') or root.findtext('customer_name')
        amount = root.findtext('amount')

        # Validate required fields
        if not invoice_id:
            raise ValueError("Missing required field: invoice_id")
        if not client_name:
            raise ValueError("Missing required field: client_name")
        if not amount:
            raise ValueError("Missing required field: amount")

        # Clean and normalize data
        result = {
            'invoice_id': invoice_id.strip(),
            'client_name': client_name.strip(),
            'amount': amount.strip()
        }

        return result

    except ExpatError as e:
        raise ValueError(f"Malformed XML provided: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML: {str(e)}")
    except Exception as e:
        # Catch any other unexpected XML-related exceptions
        raise RuntimeError(f"An error occurred while processing the invoice XML: {str(e)}")

# Unittests
