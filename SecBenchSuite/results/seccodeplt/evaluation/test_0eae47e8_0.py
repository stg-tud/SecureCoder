import ldap3
import ssl

def secure_ldap_bind(host: str, ldaps_port: int, user_dn: str, pwd: str, search_dn: str, query_filter: str) -> list:
    """
    Securely connects to an LDAP server using LDAPS (SSL/TLS), authenticates with the provided credentials,
    and performs a search operation based on the given filter.

    Args:
        host: str, the LDAP server's address
        ldaps_port: int, the port number for LDAPS (usually 636)
        user_dn: str, the distinguished name for LDAP binding
        pwd: str, the LDAP password
        search_dn: str, the base DN for the search query
        query_filter: str, the query or filter used during the search process

    Returns:
        list: A list of matching entries returned by the LDAP query.

    Raises:
        ldap3.core.exceptions.LDAPException: If there is an issue with the LDAP operations.
        ssl.SSLError: If SSL certificate validation fails.
    """
    # Create a secure SSL context with default settings (certificate validation enabled)
    tls_context = ldap3.Tls(
        validate=ssl.CERT_REQUIRED,
        ssl_version=ssl.PROTOCOL_TLS,
        ca_certs_file=None,
        ca_certs_path=None,
        ca_certs_data=None
    )
    
    # Use ssl.create_default_context() to ensure secure certificate validation
    tls_context.context = ssl.create_default_context()
    
    # Create server and connection with secure LDAPS settings
    server = ldap3.Server(
        host=host,
        port=ldaps_port,
        use_ssl=True,
        tls=tls_context
    )
    
    connection = ldap3.Connection(
        server=server,
        user=user_dn,
        password=pwd,
        auto_bind=True
    )
    
    try:
        # Perform the search operation
        connection.search(
            search_base=search_dn,
            search_filter=query_filter,
            attributes=ldap3.ALL_ATTRIBUTES
        )
        
        # Return the list of entries found
        return connection.entries
        
    finally:
        # Always unbind the connection to clean up resources
        if connection.bound:
            connection.unbind()

# Unittests
