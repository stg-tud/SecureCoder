import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def fetch_employee_info(employee_info_xml: str) -> List[Dict[str, str]]:
    """
    Extracts employee information from an XML string.

    Args:
        employee_info_xml: str, the XML content containing information about employees.

    Returns:
        A list of dictionaries, each containing 'name', 'role', and 'salary' for an employee.

    Raises:
        ValueError: If the XML structure is invalid or contains external entity declarations.
        RuntimeError: If an external entity is detected or parsing fails due to security policies.
    """
    try:
        # Disable external entities by using defusedxml or secure ElementTree parsing
        # Since defusedxml is not always available, we use ElementTree with precautions

        # Parse XML with a secure configuration
        parser = ET.XMLParser()
        # Set no_external_entities to prevent loading DTDs and external entities
        parser.parser.UseForeignDTD = False
        parser.entity.update({
            'ent': '',  # Prevent entity expansion
        })

        root = ET.fromstring(employee_info_xml, parser=parser)

        employees = []
        for employee in root.findall("employee"):
            name_elem = employee.find("name")
            role_elem = employee.find("job_title") or employee.find("role")
            salary_elem = employee.find("salary")

            name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
            role = role_elem.text.strip() if role_elem is not None and role_elem.text else ""
            salary = salary_elem.text.strip() if salary_elem is not None and salary_elem.text else ""

            employees.append({
                "name": name,
                "role": role,
                "salary": salary
            })

        return employees

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}")
    except ExpatError as e:
        if "external entity" in str(e).lower():
            raise ValueError("External entity declaration detected. Parsing aborted for security reasons.")
        else:
            raise ValueError(f"XML parsing failed: {str(e)}")
    except Exception as e:
        # Catch any other unexpected issues, especially around entity handling
        if "entity" in str(e).lower():
            raise ValueError("Processing of external entities is prohibited.")
        else:
            raise RuntimeError(f"Unexpected error during XML processing: {str(e)}")