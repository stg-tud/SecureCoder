import ssl
from ldap3 import Server, Connection, ALL, Tls
from ldap3.core.exceptions import LDAPException


def initialize_ldap_conn(
    ldap_host: str,
    server_port: int,
    user_dn: str,
    user_password: str,
    search_dn: str,
    ldap_query: str
) -> list:
    """
    Securely connects to an LDAP server using LDAPS (LDAP over SSL/TLS), authenticates
    with the provided credentials, and performs a search operation using the given filter.

    Parameters:
        ldap_host: str - The address of the target LDAP server.
        server_port: int - The port number for LDAPS (typically 636).
        user_dn: str - The distinguished name used for binding/authentication.
        user_password: str - The password associated with the bind DN.
        search_dn: str - The base DN from which to start the search.
        ldap_query: str - The LDAP filter string to apply in the search.

    Returns:
        list: A list of dictionaries representing the LDAP entries that match the search filter.

    Raises:
        ldap3.core.exceptions.LDAPException: If any LDAP operation fails.
        ssl.SSLError: If SSL certificate validation fails during connection.
    """
    # Create a secure SSL context with certificate verification enabled
    tls_context = Tls(
        ssl_version=ssl.PROTOCOL_TLS,
        validate=ssl.CERT_REQUIRED,
        ca_certs_file=None,
        ca_certs_data=None
    )
    
    # Use create_default_context to ensure proper certificate verification
    ssl_context = ssl.create_default_context()
    tls_context.ssl_context = ssl_context

    # Define the server with LDAPS and secure TLS settings
    server = Server(
        host=ldap_host,
        port=server_port,
        use_ssl=True,  # Enforce LDAPS
        tls=tls_context
    )

    # Establish connection with user credentials
    conn = Connection(
        server=server,
        user=user_dn,
        password=user_password,
        auto_bind=True  # Automatically binds upon connection
    )

    try:
        # Perform the search operation
        conn.search(
            search_base=search_dn,
            search_filter=ldap_query,
            attributes=[]  # Retrieves all attributes by default
        )

        # Return the list of entries found
        return conn.entries

    except LDAPException:
        # Re-raise LDAP exceptions as-is
        raise
    except ssl.SSLError:
        # Re-raise SSL errors as-is
        raise
    finally:
        # Ensure connection is properly closed
        conn.unbind()

# Unittests
