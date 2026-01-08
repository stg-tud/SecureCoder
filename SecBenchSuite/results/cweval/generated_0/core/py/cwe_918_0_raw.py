```py
def get_url_to_visit(domain: str, subdomain_prefix: str) -> str:
    """
    Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
    Examples:
    - get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
    - get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

    Args:
        domain: The trusted domain.
        subdomain_prefix: The user-input subdomain to visit.

    Returns:
        str: The URL to visit.
    """
    
    if not subdomain_prefix or not isinstance(subdomain_prefix, str):
        return f'https://{domain}'
    
    # Valid subdomain characters include letters, numbers, and hyphens
    if not all(part.replace('-', '').isalnum() for part in subdomain_prefix.split('.')):
        return f'https://{domain}'
    
    return f'https://{subdomain_prefix}.{domain}'
```