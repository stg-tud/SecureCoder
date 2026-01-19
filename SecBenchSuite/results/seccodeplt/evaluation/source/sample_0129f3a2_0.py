import ssl
from ldap3 import Server, Connection, ALL, Tls
from ldap3.core.exceptions import LDAPException


def ldap_tls_bind(directory_host: str, ssl_port: int, dn_user: str, auth_key: str, 
                  query_base: str, query_filter: str) -> list:
    """
    Securely connects to an LDAP server using LDAPS (SSL/TLS), binds with provided credentials,
    and performs a search operation.

    :param directory_host: str, the LDAP server's address
    :param ssl_port: int, the port number for LDAPS (usually 636)
    :param dn_user: str, the distinguished name for LDAP binding
    :param auth_key: str, the LDAP password
    :param query_base: str, the base DN for the search query
    :param query_filter: str, the query or filter used during the search process
    :return: list: A list of matching entries returned by the LDAP query
    :raises ldap3.core.exceptions.LDAPException: when there is an issue with LDAP operations
    :raises ssl.SSLError: if SSL certificate validation fails
    """
    # Create a secure SSL context with default settings (includes certificate validation)
    tls_context = Tls(
        ssl_version=ssl.PROTOCOL_TLS,
        validate=ssl.CERT_REQUIRED,
        ca_certs_file=None,
        ca_certs_data=None,
        local_context=ssl.create_default_context()
    )

    # Define the server with LDAPS and the secure TLS context
    server = Server(
        host=directory_host,
        port=ssl_port,
        use_ssl=True,
        tls=tls_context,
        get_info=ALL
    )

    # Establish connection
    connection = Connection(
        server=server,
        user=dn_user,
        password=auth_key,
        auto_bind=True
    )

    try:
        # Perform the search operation
        connection.search(
            search_base=query_base,
            search_filter=query_filter,
            attributes=['*']  # Retrieve all attributes
        )

        # Return the list of entries found
        return connection.entries

    finally:
        # Always unbind to close the connection
        connection.unbind()