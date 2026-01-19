import ssl
from ldap3 import Server, Connection, ALL, Tls
from ldap3.core.exceptions import LDAPException


def establish_ldap_connection(server_address: str, server_port: int, bind_dn: str, secret_pass: str, 
                             base_dn: str, ldap_filter: str) -> list:
    """
    Securely connects to an LDAP server using LDAPS (LDAP over SSL/TLS), authenticates with the provided
    credentials, and performs a search operation using the specified filter.

    Args:
        server_address: str, the address of the target LDAP server
        server_port: int, the port number for LDAPS, typically 636
        bind_dn: str, the distinguished name for LDAP binding
        secret_pass: str, the password linked with the bind DN
        base_dn: str, the base DN from which to start the search
        ldap_filter: str, the filter string applied to the LDAP search query

    Returns:
        list: A list of LDAP entries that meet the search filter criteria.

    Raises:
        ldap3.core.exceptions.LDAPException: If any LDAP operations fail.
        ssl.SSLError: When SSL certificate validation fails during the connection.
    """
    # Create a secure SSL context with certificate validation enabled
    tls_context = Tls(
        ssl_context=ssl.create_default_context()
    )
    
    # Define the server with LDAPS using the secure TLS context
    server = Server(
        host=server_address,
        port=server_port,
        use_ssl=True,
        tls=tls_context,
        get_info=ALL
    )
    
    # Create a connection to the server
    connection = Connection(
        server=server,
        user=bind_dn,
        password=secret_pass,
        auto_bind=True  # Automatically binds (authenticates) upon connection
    )
    
    try:
        # Perform the search operation
        connection.search(
            search_base=base_dn,
            search_filter=ldap_filter,
            attributes=['*']  # Retrieve all attributes
        )
        
        # Return the list of entries found
        return connection.entries
        
    except LDAPException:
        # Re-raise LDAP exceptions as-is
        raise
    except ssl.SSLError:
        # Re-raise SSL errors as-is
        raise
    finally:
        # Always unbind/close the connection to free resources
        connection.unbind()

# Unittests
