import ldap3
import ssl

def ldap_secure_bind(server_host: str, server_port: int, dn: str, bind_pass: str, 
                    search_dn: str, search_filter: str) -> list:
    """
    Connects securely to an LDAP server using LDAPS (LDAP over SSL/TLS), authenticates
    with the provided credentials, and executes a search query.

    Args:
        server_host: str, the hostname or IP address of the LDAP server
        server_port: int, the port number used for LDAPS (commonly 636)
        dn: str, distinguished name for authentication
        bind_pass: str, the password corresponding to the dn
        search_dn: str, the starting point for the search query
        search_filter: str, the LDAP search filter to be used

    Returns:
        list: A list containing entries that match the search filter.

    Raises:
        ldap3.core.exceptions.LDAPException: In case of any LDAP operation issue.
        ssl.SSLError: For SSL certificate validation problems.
    """
    # Create SSL context with default settings for certificate verification
    ssl_context = ssl.create_default_context()

    # Configure the LDAP server with TLS using the SSL context
    server = ldap3.Server(
        host=server_host,
        port=server_port,
        use_ssl=True,
        tls=ldap3.Tls(ssl_context=ssl_context)
    )

    # Create a connection with authentication
    connection = ldap3.Connection(
        server=server,
        user=dn,
        password=bind_pass,
        auto_bind=True
    )

    try:
        # Execute the search query
        connection.search(
            search_base=search_dn,
            search_filter=search_filter,
            attributes=ldap3.ALL_ATTRIBUTES
        )

        # Return the list of entries found
        return connection.entries
    finally:
        # Always unbind the connection to clean up
        connection.unbind()

# Unittests
