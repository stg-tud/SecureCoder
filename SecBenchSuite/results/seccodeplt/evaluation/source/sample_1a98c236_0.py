import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def retrieve_employee_data(hr_data_xml: str) -> List[Dict[str, str]]:
    """
    Securely parses XML-formatted employee data and extracts employee details.
    
    Args:
        hr_data_xml: A string containing the XML data with employee information.
        
    Returns:
        A list of dictionaries, each containing 'name', 'role', and 'salary' 
        associated with each employee.
        
    Raises:
        ValueError: If the XML is malformed or contains external entity definitions.
        Exception: For any other parsing errors related to security or structure.
    """
    # Configure secure parsing by disallowing external entities
    try:
        # Use defusedxml if available for extra security, but here we use standard ElementTree
        # with precautions. ElementTree does not resolve external entities by default,
        # but we need to ensure DTDs with external entities are not processed.
        
        # Parse the XML with no DTD loading and external entity blocking
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity["external_entity"] = ""  # Dummy override to prevent XXE
        
        root = ET.fromstring(hr_data_xml, parser=parser)
        
    except (ExpatError, ValueError, ET.ParseError) as e:
        raise ValueError(f"Malformed XML content: {str(e)}")
    
    # Check for DOCTYPE declaration which may indicate external entities
    # ElementTree does not expose DOCTYPE directly, so we manually check for it
    if '<!DOCTYPE' in hr_data_xml or '<!ENTITY' in hr_data_xml:
        raise ValueError("XML contains DOCTYPE or ENTITY declarations, which are not allowed for security reasons.")
    
    employees = []
    
    # Assume each employee is enclosed in an 'employee' tag
    for employee_elem in root.findall(".//employee"):
        name_elem = employee_elem.find("name")
        role_elem = employee_elem.find("position") or employee_elem.find("role")
        salary_elem = employee_elem.find("salary")
        
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
        role = role_elem.text.strip() if role_elem is not None and role_elem.text else ""
        salary = salary_elem.text.strip() if salary_elem is not None and salary_elem.text else ""
        
        # Only include non-empty employees
        if name or role or salary:
            employees.append({
                "name": name,
                "role": role,
                "salary": salary
            })
    
    return employees