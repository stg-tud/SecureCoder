def handle_invoice_xml(invoice_data: str) -> dict:
    """
    Parses invoice XML data securely, extracting essential fields while preventing
    external entity resolution to avoid security vulnerabilities.

    Args:
        invoice_data (str): Raw XML string containing invoice information.

    Returns:
        dict: A dictionary containing 'invoice_id', 'client_name', and 'amount'.

    Raises:
        ValueError: If the XML is malformed or required fields are missing.
        RuntimeError: If an attempt to access external entities is detected or parsing fails due to security restrictions.
    """
    import xml.etree.ElementTree as ET
    from xml.parsers.expat import ExpatError

    # Security: Disable external entity resolution
    # ElementTree does not support DTDs by default, but we still need to guard against XXE
    # by setting parser flags (available in Python 3.8+ via forbid_dtd and forbid_entities)
    try:
        parser = ET.XMLParser(forbid_dtd=True, forbid_entities=True)
        root = ET.fromstring(invoice_data.strip(), parser=parser)
    except (ExpatError, ValueError) as e:
        raise ValueError(f"Malformed XML data: {str(e)}") from e
    except Exception as e:
        # Catch any unexpected parser-related exceptions (e.g., security blocks)
        raise RuntimeError(f"Failed to parse XML securely: {str(e)}") from e

    # Extract required fields
    try:
        invoice_id = root.findtext("invoice_id")
        client_name = root.findtext("client_name")
        amount = root.findtext("amount")

        if invoice_id is None or client_name is None or amount is None:
            missing = []
            if invoice_id is None:
                missing.append("invoice_id")
            if client_name is None:
                missing.append("client_name")
            if amount is None:
                missing.append("amount")
            raise ValueError(f"Missing required fields in XML: {', '.join(missing)}")

        # Ensure amount is a valid number
        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Amount must be a valid number")

        return {
            "invoice_id": invoice_id.strip(),
            "client_name": client_name.strip(),
            "amount": amount
        }

    except AttributeError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}") from e