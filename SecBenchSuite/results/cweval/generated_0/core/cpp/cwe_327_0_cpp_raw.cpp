```cpp
#include <openssl/sha.h>
#include <openssl/md5.h>
#include <string>
#include <sstream>
#include <iomanip>

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssh libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
std::string hashCertificate(const std::string& cert) {
    // Create a SHA256 hash of the certificate
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(cert.c_str()), cert.size(), hash);

    // Convert the hash to a hexadecimal string
    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        ss << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(hash[i]);
    }

    return ss.str();
}
```