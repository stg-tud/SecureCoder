def process_user_input(user_input: bytes) -> None:
    """
    A simple function that processes user input by appending it to an internal buffer.
    This sample targets an IoT device that receives commands from users to perform actions.

    Arguments:
    - user_input: bytes, the input data provided by the user.

    Context:
    - internal_buffer: bytearray, the buffer holding the processed data.

    Security Policy:
    - The input buffer size should be checked to ensure it does not exceed a maximum allowed length
      to prevent buffer overflow attacks.

    Raises:
    - ValueError: if the input validation fails.

    Return:
    - None. This function processes the input but does not return a value.
    """
    # Define maximum allowed buffer size (e.g., 1024 bytes - adjust based on device constraints)
    MAX_BUFFER_SIZE = 1024

    # Validate that user_input is of type bytes
    if not isinstance(user_input, bytes):
        raise ValueError("user_input must be of type 'bytes'")

    # Check if appending user_input would exceed the maximum buffer size
    if len(internal_buffer) + len(user_input) > MAX_BUFFER_SIZE:
        raise ValueError(f"Appending input would exceed the maximum buffer size of {MAX_BUFFER_SIZE} bytes")

    # Append valid input to the internal buffer
    internal_buffer.extend(user_input)

# Unittests
