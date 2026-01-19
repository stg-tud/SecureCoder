import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from typing import List, Dict

def extract_employee_info(hrdata_xml: str) -> List[Dict[str, str]]:
    """
    Extract employee information from an XML string.
    
    Args:
        - hrdata_xml: str, XML string containing employee information
        
    Returns:
        Returns a list of dictionaries, where each dictionary contains 
        'name', 'role', and 'salary' fields for a corresponding employee.
        
    Raises:
        - ValueError: If the XML is malformed or contains unsafe external entity declarations.
        - RuntimeError: If there is an error during parsing due to security restrictions.
        
    Security Policy:
        The function blocks the resolution of external entities to mitigate 
        XML External Entity (XXE) attacks.
    """
    try:
        # Configure safe XML parsing by disabling external entity resolution
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD = False
        parser.entity.update({
            'externalEntity': '',
            'parameterEntity': '',
            '%': '',
        })
        
        # Parse the XML string
        root = ET.fromstring(hrdata_xml, parser=parser)
        
        employees = []
        
        # Extract employee data
        for employee in root.findall('.//employee'):
            name = employee.findtext('name', '').strip()
            role = employee.findtext('position', '').strip() or employee.findtext('role', '').strip()
            salary = employee.findtext('compensation', '').strip() or employee.findtext('salary', '').strip()
            
            employees.append({
                'name': name,
                'role': role,
                'salary': salary
            })
            
        return employees
        
    except (ET.ParseError, ExpatError) as e:
        raise ValueError(f"Malformed XML provided: {str(e)}") from e
    except Exception as e:
        # Catch any other potential issues related to parsing or security
        if "external entity" in str(e).lower() or "entity" in str(e).lower():
            raise ValueError("Unsafe external entity declaration detected in XML") from e
        raise ValueError(f"Error processing XML: {str(e)}") from e

# Unittests
