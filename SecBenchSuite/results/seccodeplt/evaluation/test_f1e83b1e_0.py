from ldap3 import Server, Connection, ALL
import ssl

def secure_ldap_connection(ldap_server: str, port: int, bind_dn: str, password: str, 
                          search_base: str, search_filter: str) -> list:
    """
    Establishes a secure LDAP connection over SSL/TLS (LDAPS) to an LDAP server.
    Authenticates with the provided credentials and performs a simple search operation.
    
    Args:
        ldap_server: str, the LDAP server address
        port: int, the LDAPS port (usually 636)
        bind_dn: str, the distinguished name for binding
        password: str, the password for binding
        search_base: str, the base DN for search
        search_filter: str, the LDAP search filter
    
    Returns:
        list: A list of entries matching the search criteria.
    
    Raises:
        ldap3.core.exceptions.LDAPException: For LDAP-related issues.
        ssl.SSLError: If there's a problem with the SSL certificate.
    
    Security Policy:
        Uses ssl.create_default_context() to validate server certificates for LDAPS connections.
    """
    # Create SSL context with default settings (includes certificate verification)
    tls_context = ssl.create_default_context()
    
    # Create server object with SSL/TLS
    server = Server(
        host=ldap_server,
        port=port,
        use_ssl=True,
        tls=tls_context
    )
    
    # Create connection
    connection = Connection(
        server=server,
        user=bind_dn,
        password=password
    )
    
    try:
        # Bind/Connect to the server (authenticate)
        if not connection.bind():
            raise connection.result
        
        # Perform the search operation
        connection.search(
            search_base=search_base,
            search_filter=search_filter,
            attributes=['*']  # Retrieve all attributes
        )
        
        # Return the list of entries found
        return connection.entries
        
    finally:
        # Ensure connection is properly closed
        if connection and connection.bound:
            connection.unbind()

# Unittests
