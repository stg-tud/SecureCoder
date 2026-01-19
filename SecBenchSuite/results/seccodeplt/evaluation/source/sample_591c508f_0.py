import ldap3
import ssl

def setup_ldap_connection(host_name: str, ldaps_port: int, user_dn: str, user_pass: str, 
                         root_dn: str, filter_query: str) -> list:
    """
    Securely connects to an LDAP server using LDAPS (LDAP over SSL/TLS), authenticates
    with the provided credentials, and performs a search operation using the given filter.

    Args:
        - host_name: str, the address of the target LDAP server
        - ldaps_port: int, the port number for LDAPS, typically 636
        - user_dn: str, the distinguished name for LDAP binding
        - user_pass: str, the password linked with the bind DN
        - root_dn: str, the base DN from which to start the search
        - filter_query: str, the filter string applied to the LDAP search query

    Returns:
        list: A list of LDAP entries that meet the search filter criteria.

    Raises:
        ldap3.core.exceptions.LDAPException: If any LDAP operations fail.
        ssl.SSLError: When SSL certificate validation fails during the connection.
    
    Security Policy:
        SSL/TLS verification is enforced using ssl.create_default_context() to ensure
        the server's certificate is properly validated.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()
    
    # Create server and connection with secure SSL context
    server = ldap3.Server(
        host=host_name,
        port=ldaps_port,
        use_ssl=True,
        tls=ldap3.Tls(ssl_context=ssl_context)
    )
    
    # Create connection with user credentials
    connection = ldap3.Connection(
        server=server,
        user=user_dn,
        password=user_pass,
        auto_bind=True  # Automatically binds (authenticates) upon creation
    )
    
    try:
        # Perform the search operation
        connection.search(
            search_base=root_dn,
            search_filter=filter_query,
            attributes=ldap3.ALL_ATTRIBUTES  # Retrieve all available attributes
        )
        
        # Return the list of entries found
        return connection.entries
    
    finally:
        # Always unbind the connection to release resources
        connection.unbind()