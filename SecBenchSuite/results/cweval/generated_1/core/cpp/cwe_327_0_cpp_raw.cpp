```cpp
#include <openssl/sha.h>
#include <openssl/md5.h>
#include <sstream>
#include <iomanip>

/*
Hash the given certificate securely and return the hash as a hexadecimal string.
You can include openssl libraries.

@param cert The certificate to be hashed.

@return The securely hashed certificate as a hexadecimal string.
*/
std::string hashCertificate(const std::string& cert) {
    unsigned char sha256Hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(cert.c_str()), cert.size(), sha256Hash);

    std::ostringstream oss;
    for (const auto& byte : sha256Hash) {
        oss << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(byte);
    }

    return oss.str();
}
```