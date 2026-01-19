if os.path.exists(tmp_file_path):
    os.remove(tmp_file_path)  # Vulnerable to TOCTOU (Time-of-Check to Time-of-Use)