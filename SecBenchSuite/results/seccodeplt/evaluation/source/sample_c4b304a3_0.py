import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def parse_staff_data(staff_xml: str) -> List[Dict[str, str]]:
    """
    Safely parse XML string containing employee information and extract name, role, and salary.
    
    Args:
        staff_xml: str, XML string containing employee information
        
    Returns:
        List of dictionaries with 'name', 'role', and 'salary' fields for each employee
        
    Raises:
        ValueError: If the XML is malformed or contains external entity declarations
        RuntimeError: If an error occurs during parsing
    """
    try:
        # Configure secure parsing by using a custom parser that disables DTD processing
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(False)
        parser.entity.update({
            '': None,
        })
        
        # Parse the XML string with secure settings
        root = ET.fromstring(staff_xml, parser=parser)
        
        employees = []
        
        # Find all employee elements (case-insensitive approach for common tags)
        employee_elements = root.findall(".//employee") or root.findall(".//Employee") or root.findall(".//EMPLOYEE")
        
        if len(employee_elements) == 0 and root.tag.lower() == 'employee':
            employee_elements = [root]
            
        for emp in employee_elements:
            employee_data = {
                'name': '',
                'role': '',
                'salary': ''
            }
            
            # Extract name from common variations
            name_elem = (emp.find('name') or emp.find('Name') or 
                        emp.find('NAME') or emp.find('fullName') or
                        emp.find('full_name'))
            if name_elem is not None and name_elem.text:
                employee_data['name'] = name_elem.text.strip()
                
            # Extract role/position from common variations
            role_elem = (emp.find('role') or emp.find('Role') or
                        emp.find('ROLE') or emp.find('position') or
                        emp.find('Position') or emp.find('POSITION'))
            if role_elem is not None and role_elem.text:
                employee_data['role'] = role_elem.text.strip()
                
            # Extract salary/compensation from common variations
            salary_elem = (emp.find('salary') or emp.find('Salary') or
                          emp.find('SALARY') or emp.find('compensation') or
                          emp.find('Compensation') or emp.find('COMPENSATION'))
            if salary_elem is not None and salary_elem.text:
                employee_data['salary'] = salary_elem.text.strip()
                
            employees.append(employee_data)
            
        return employees
        
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {str(e)}") from e
    except ExpatError as e:
        raise ValueError(f"XML parsing error: {str(e)}") from e
    except Exception as e:
        # Catch any potential entity resolution attempts or other issues
        if "entity" in str(e).lower():
            raise ValueError(f"Unsafe external entity detected in XML") from e
        raise RuntimeError(f"Error processing XML: {str(e)}") from e