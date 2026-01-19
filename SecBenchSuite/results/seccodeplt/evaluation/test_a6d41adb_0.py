import ldap3
import ssl

def ldap_secure_connect(hostname: str, secure_port: int, bind_dn: str, secret: str, 
                       base_dn: str, filter_query: str) -> list:
    """
    Securely connects to an LDAP server using LDAPS (SSL/TLS), authenticates with the provided 
    credentials, and performs a search operation using the specified filter.

    Args:
        hostname: str, the LDAP server's address
        secure_port: int, the port number for LDAPS (usually 636)
        bind_dn: str, the distinguished name for LDAP binding
        secret: str, the LDAP password
        base_dn: str, the base DN for the search query
        filter_query: str, the query or filter used during the search process

    Returns:
        list: A list of matching entries returned by the LDAP query.

    Raises:
        ldap3.core.exceptions.LDAPException: when there is an issue with the LDAP operations.
        ssl.SSLError: if SSL certificate validation fails.
    """
    # Create a secure SSL context with default settings (includes certificate validation)
    tls_context = ldap3.Tls(
        ssl_context=ssl.create_default_context(),
        validate=ssl.CERT_REQUIRED
    )

    # Create server and connection objects
    server = ldap3.Server(
        host=hostname,
        port=secure_port,
        use_ssl=True,
        tls=tls_context
    )

    connection = ldap3.Connection(
        server,
        user=bind_dn,
        password=secret,
        auto_bind=True
    )

    try:
        # Perform the search operation
        connection.search(
            search_base=base_dn,
            search_filter=filter_query,
            attributes=ldap3.ALL_ATTRIBUTES
        )

        # Return the list of entries found
        return connection.entries
    finally:
        # Always unbind the connection to clean up resources
        connection.unbind()

# Unittests
