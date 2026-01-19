import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def get_employee_data(employee_details_xml: str) -> List[Dict[str, str]]:
    """
    Safely parse XML string containing employee details and extract name, role, and salary.
    
    Args:
        employee_details_xml: str, XML string containing employee information
        
    Returns:
        List of dictionaries with keys 'name', 'role', and 'salary' for each employee
        
    Raises:
        ValueError: If the XML is malformed or contains external entity declarations
        RuntimeError: If a potential XXE attack is detected
    """
    if not employee_details_xml or not employee_details_xml.strip():
        raise ValueError("XML input is empty or None")
    
    try:
        # Parse XML with safe configuration
        # ElementTree does not resolve external entities by default, but we want to be extra cautious
        
        # First, check for potential XXE patterns in the XML string
        suspicious_patterns = ['<!DOCTYPE', '<!ENTITY', 'SYSTEM', 'PUBLIC']
        xml_lower = employee_details_xml.lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in xml_lower:
                raise ValueError(f"Potential XXE vulnerability detected: {pattern} found in XML")
        
        # Parse the XML
        root = ET.fromstring(employee_details_xml)
        
        employees = []
        
        # Assuming employee data is in elements named 'employee' or similar structure
        # This handles common structures like <employees><employee>...</employee></employees>
        # or just multiple <employee>...</employee> elements
        
        employee_elements = []
        
        # Check if root is 'employees' or similar container
        if root.tag.lower() in ['employees', 'staff', 'team']:
            employee_elements = root.findall('employee')
        elif root.tag.lower() == 'employee':
            # Single employee case
            employee_elements = [root]
        else:
            # Try to find all employee elements regardless of root
            employee_elements = root.findall('.//employee') or [root]
        
        for emp in employee_elements:
            employee_data = {
                'name': '',
                'role': '',
                'salary': ''
            }
            
            # Extract name - check common variations
            for tag in ['name', 'fullname', 'employee_name', 'first_name', 'lastname']:
                field = emp.find(tag)
                if field is not None and field.text:
                    if tag in ['first_name', 'lastname']:
                        # Handle first/last name separately if needed
                        if not employee_data['name']:
                            employee_data['name'] = field.text
                        else:
                            employee_data['name'] += f" {field.text}"
                    else:
                        employee_data['name'] = field.text.strip()
                    break
            
            # Extract role/position - check common variations
            for tag in ['role', 'position', 'title', 'job_title', 'designation']:
                field = emp.find(tag)
                if field is not None and field.text:
                    employee_data['role'] = field.text.strip()
                    break
            
            # Extract salary/compensation - check common variations
            for tag in ['salary', 'compensation', 'pay', 'wage', 'compensation_amount']:
                field = emp.find(tag)
                if field is not None and field.text:
                    employee_data['salary'] = field.text.strip()
                    break
            
            employees.append(employee_data)
        
        return employees
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}")
    except Exception as e:
        # Catch any other unexpected XML parsing issues
        if "entity" in str(e).lower():
            raise ValueError(f"External entity processing error: {str(e)}")
        raise ValueError(f"Error processing XML: {str(e)}")

# Unittests
