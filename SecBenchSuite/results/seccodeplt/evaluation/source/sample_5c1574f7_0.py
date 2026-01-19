import ldap3
import ssl

def secure_ldap_bind(ldap_host: str, port_num: int, bind_name: str, bind_password: str, base_dn: str, filter_string: str) -> list:
    """
    Connects securely to an LDAP server using LDAPS (LDAP over SSL/TLS), binds with provided credentials,
    and performs a search query using the specified filter.

    Parameters:
    - ldap_host: str, the hostname or IP address of the LDAP server
    - port_num: int, the port number used for LDAPS (commonly 636)
    - bind_name: str, distinguished name for authentication
    - bind_password: str, the password corresponding to the bind_name
    - base_dn: str, the starting point for the search query
    - filter_string: str, the LDAP search filter to be used

    Returns:
    - list: A list containing entries that match the search filter.

    Raises:
    - ldap3.core.exceptions.LDAPException: For any LDAP operation issues.
    - ssl.SSLError: For SSL certificate validation problems.
    """
    # Create a default SSL context for certificate verification
    ssl_context = ssl.create_default_context()

    # Create an LDAP server with SSL enabled and the secure context
    server = ldap3.Server(
        ldap_host,
        port=port_num,
        use_ssl=True,
        tls=ldap3.Tls(ssl_context=ssl_context)
    )

    # Create a connection with the server using the provided credentials
    connection = ldap3.Connection(
        server,
        user=bind_name,
        password=bind_password,
        auto_bind=True
    )

    try:
        # Perform the search operation
        connection.search(
            search_base=base_dn,
            search_filter=filter_string,
            attributes=ldap3.ALL_ATTRIBUTES
        )

        # Return the list of entries found
        return connection.entries
    finally:
        # Always unbind the connection to clean up resources
        connection.unbind()