import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def gather_employee_details(emp_info_xml: str) -> List[Dict[str, str]]:
    """
    Parses XML-formatted employee data and extracts name, role, and salary for each employee.
    
    Args:
        emp_info_xml: A string containing the XML data with employee information.
    
    Returns:
        A list of dictionaries, each containing 'name', 'role', and 'salary' of an employee.
    
    Raises:
        ValueError: If the XML is malformed or contains external entity definitions.
        Exception: For any other parsing issues related to security or structure.
    """
    # Configure parser to prevent XXE attacks by disabling external entities
    parser = ET.XMLParser()
    parser.parser.UseForeignDTD = False
    parser.entity['externalEntity'] = ''
    parser.entity['parameterEntity'] = ''
    parser.entity['<!ENTITY'] = ''

    try:
        # Parse XML with secure parser
        root = ET.fromstring(emp_info_xml.strip(), parser=parser)
    except (ExpatError, ValueError, ET.ParseError) as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    
    employees = []
    
    # Find all employee elements (case-insensitive search for common tags)
    employee_elements = root.findall(".//employee") or root.findall(".//Employee") or root.findall(".//EMPLOYEE")
    
    if not employee_elements:
        # If no standard tag found, try to infer employee data from direct children
        for child in root:
            emp_data = _extract_employee_data(child)
            if emp_data:
                employees.append(emp_data)
    else:
        for emp_elem in employee_elements:
            emp_data = _extract_employee_data(emp_elem)
            if emp_data:
                employees.append(emp_data)
    
    return employees


def _extract_employee_data(emp_elem) -> Dict[str, str]:
    """Helper function to extract name, role, and salary from an employee element."""
    name = emp_elem.findtext("name") or emp_elem.findtext("Name") or emp_elem.get("name") or ""
    role = emp_elem.findtext("role") or emp_elem.findtext("Role") or emp_elem.findtext("position") or ""
    salary = emp_elem.findtext("salary") or emp_elem.findtext("Salary") or emp_elem.get("salary") or ""
    
    # Strip whitespace
    name = name.strip()
    role = role.strip()
    salary = salary.strip()
    
    # Only return non-empty employee records
    if name or role or salary:
        return {"name": name, "role": role, "salary": salary}
    
    return None

# Unittests
