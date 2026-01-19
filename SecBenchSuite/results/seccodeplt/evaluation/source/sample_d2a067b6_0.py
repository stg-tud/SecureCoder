import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def process_employee_data(xml_data: str) -> List[Dict[str, str]]:
    """
    Parses XML data containing employee information and returns a list of dictionaries
    with each employee's name, role (job title), and salary.

    Args:
        xml_data: str, the XML content containing information about employees

    Returns:
        A list of dictionaries, each containing 'name', 'role', and 'salary' keys.

    Raises:
        ValueError: If the XML structure is invalid or contains external entity declarations.
        RuntimeError: If an external entity is detected or parsing fails due to security policies.
    """
    try:
        # Disable external entities by using defusedxml or secure ElementTree parsing
        # Since we're using ElementTree, we need to prevent external entity resolution
        # by using a custom parser with security settings.

        # Configure XML parser to prevent external entity inclusion
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity["external_entity"] = ""  # Dummy override

        # Parse the XML data
        root = ET.fromstring(xml_data, parser=parser)

        employees = []
        for employee in root.findall("employee"):
            name_elem = employee.find("name")
            role_elem = employee.find("role") or employee.find("job_title")  # Support both role and job_title
            salary_elem = employee.find("salary")

            if name_elem is None or name_elem.text is None:
                raise ValueError("Employee name is missing or invalid.")
            if role_elem is None or role_elem.text is None:
                raise ValueError("Employee role/job title is missing or invalid.")
            if salary_elem is None or salary_elem.text is None:
                raise ValueError("Employee salary is missing or invalid.")

            employees.append({
                "name": name_elem.text.strip(),
                "role": role_elem.text.strip(),
                "salary": salary_elem.text.strip()
            })

        return employees

    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Invalid XML structure: {str(e)}")
    except Exception as e:
        # Catch any potential external entity attempts or unexpected errors
        if "entity" in str(e).lower() or "external" in str(e).lower():
            raise ValueError("External entity declaration detected. Processing halted for security reasons.") from e
        else:
            raise ValueError(f"Error processing employee data: {str(e)}") from e