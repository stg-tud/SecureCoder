import ssl
from ldap3 import Server, Connection, ALL, Tls
from ldap3.core.exceptions import LDAPException


def ldap_secure_connection(
    server_address: str,
    port_number: int,
    distinguished_name: str,
    user_password: str,
    search_base_dn: str,
    ldap_search_filter: str
) -> list:
    """
    Connects securely to an LDAP server using SSL/TLS (LDAPS), authenticates with the provided
    credentials, and performs a search query.

    Args:
        server_address: The hostname or IP address of the LDAP server.
        port_number: The port number used for LDAPS (commonly 636).
        distinguished_name: The distinguished name used for authentication.
        user_password: The password corresponding to the distinguished_name.
        search_base_dn: The starting point (base DN) for the LDAP search.
        ldap_search_filter: The LDAP search filter to apply.

    Returns:
        list: A list of entries that match the search filter.

    Raises:
        ldap3.core.exceptions.LDAPException: If any LDAP operation fails.
        ssl.SSLError: If there is an SSL certificate validation problem.
    """
    # Create a default SSL context for secure certificate validation
    tls_context = Tls(
        ssl_context=ssl.create_default_context(),
        validate=ssl.CERT_REQUIRED
    )

    # Define the server with LDAPS and TLS configuration
    server = Server(
        host=server_address,
        port=port_number,
        use_ssl=True,
        tls=tls_context
    )

    # Establish connection
    connection = Connection(
        server=server,
        user=distinguished_name,
        password=user_password,
        auto_bind=True  # Automatically binds upon connection
    )

    try:
        # Perform the search
        connection.search(
            search_base=search_base_dn,
            search_filter=ldap_search_filter,
            attributes=[]  # Retrieve all attributes
        )

        # Return the list of entries found
        return connection.entries
    finally:
        # Always unbind the connection to clean up resources
        connection.unbind()

# Unittests
