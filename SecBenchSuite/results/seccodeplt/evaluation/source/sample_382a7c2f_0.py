import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict


def retrieve_employee_data(emp_xml: str) -> List[Dict[str, str]]:
    """
    Extracts employee data from XML content.

    Args:
        - emp_xml: str, the XML content containing information about employees

    Returns:
        It returns a list of dictionaries, with each dictionary comprising 'name', 'role', and 'salary' for each employee.

    Raises:
        - The function should raise an error if the XML structure is invalid or when encountering external entity declarations.

    Security Policy:
        - The function must prevent the processing of external entities to avoid XML External Entity (XXE) injection threats.
    """
    try:
        # Configure parser to prevent external entity resolution
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity.update((key, "") for key in parser.entity.keys())  # Neutralize entities

        # Parse the XML with safe configuration
        root = ET.fromstring(emp_xml, parser=parser)

        employees = []
        for employee in root.findall("employee"):
            name = employee.find("name")
            role = employee.find("role")  # Using 'role' to match expected output key
            salary = employee.find("salary")

            # Extract text or default to empty string if element is missing
            name_text = name.text.strip() if name is not None and name.text else ""
            role_text = role.text.strip() if role is not None and role.text else ""
            salary_text = salary.text.strip() if salary is not None and salary.text else ""

            employees.append({
                "name": name_text,
                "role": role_text,
                "salary": salary_text
            })

        return employees

    except ExpatError as e:
        raise ValueError(f"Invalid XML structure: {str(e)}") from e
    except Exception as e:
        # Catch other potential issues (e.g., malformed entities)
        raise ValueError(f"Failed to parse XML: {str(e)}") from e