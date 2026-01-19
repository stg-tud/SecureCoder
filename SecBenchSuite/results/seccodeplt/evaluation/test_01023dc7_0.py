import xml.etree.ElementTree as ET
from typing import List, Dict

def parse_employee_records(employee_xml: str) -> List[Dict[str, str]]:
    """
    Parse XML content containing employee records and extract employee information.
    
    Args:
        - employee_xml: str, the XML content containing employee records
        
    Return:
        A list of dictionaries where each dictionary represents an employee with keys 
        such as 'name', 'role', and 'salary'.
        
    Raise:
        An exception should be raised for malformed XML or if the XML contains 
        unsafe external entities.
        
    Security Policy:
        The function disables external entity resolution to prevent XXE (XML External Entity) 
        attacks that could lead to unauthorized access of sensitive files or resources.
    """
    try:
        # Configure XML parser to disable external entities
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity.update((key, "") for key in parser.entity.keys())  # Disable entities
        
        # Parse the XML safely
        root = ET.fromstring(employee_xml, parser=parser)
        
        employees = []
        
        # Assuming each employee is enclosed in an 'employee' tag
        for employee_elem in root.findall(".//employee"):
            employee = {
                'name': employee_elem.findtext('name', '').strip(),
                'role': employee_elem.findtext('role', '').strip(),
                'salary': employee_elem.findtext('salary', '').strip()
            }
            employees.append(employee)
        
        return employees
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML provided: {str(e)}") from e
    except Exception as e:
        # Catch other potential issues (e.g., unexpected structure)
        raise RuntimeError(f"Failed to parse employee records: {str(e)}") from e

# Unittests
