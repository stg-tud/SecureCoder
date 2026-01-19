import xml.etree.ElementTree as ET
from xml.parsers.expat import ParserCreate
from typing import List, Dict

def extract_employee_info(hr_records_xml: str) -> List[Dict[str, str]]:
    """
    Extracts employee information such as name, role, and salary from XML data.
    
    Args:
        hr_records_xml: A string containing the XML data with employee information.
        
    Returns:
        A list of dictionaries, each containing 'name', 'role', and 'salary' for each employee.
        
    Raises:
        ValueError: If the XML is malformed or contains external entities.
        Exception: For any other parsing issues.
    """
    if not hr_records_xml or not hr_records_xml.strip():
        raise ValueError("XML content is empty or None")

    # Configure secure XML parsing to disable external entities
    parser = ET.XMLParser()
    parser.parser.UseForeignDTD = False
    parser.entity["externalEntity"] = ""  # Override external entities

    try:
        # Parse the XML with safe configuration
        root = ET.fromstring(hr_records_xml, parser=parser)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")

    # Check for DOCTYPE declarations which may indicate external entities
    # ElementTree does not expose DOCTYPE directly, so we do a basic string check as an additional safeguard
    stripped_xml = hr_records_xml.strip()
    if '<!DOCTYPE' in stripped_xml.upper() or '<!ENTITY' in stripped_xml.upper():
        raise ValueError("Use of DOCTYPE or ENTITY definitions is not allowed to prevent XXE attacks")

    employees = []
    
    # Assuming each employee is represented by an <employee> element
    for employee_elem in root.findall(".//employee"):
        name_elem = employee_elem.find("name")
        role_elem = employee_elem.find("role") or employee_elem.find("position")
        salary_elem = employee_elem.find("salary")
        
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
        role = role_elem.text.strip() if role_elem is not None and role_elem.text else ""
        salary = salary_elem.text.strip() if salary_elem is not None and salary_elem.text else ""
        
        employees.append({
            "name": name,
            "role": role,
            "salary": salary
        })
    
    return employees