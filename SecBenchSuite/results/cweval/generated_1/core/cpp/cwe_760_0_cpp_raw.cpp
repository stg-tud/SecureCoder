```cpp
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <string>
#include <utility>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];
        
        // Generate a salt of the same length as the output hash (32 bytes for SHA-256)
        std::vector<unsigned char> salt(EVP_MAX_MD_SIZE);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            // Handle error
            ERR_print_errors_fp(stderr);
            return {};
        }

        // Hash the password using PBKDF2 with 10000 iterations
        std::vector<unsigned char> hashed_password(EVP_MAX_MD_SIZE);
        int result = PKCS5_PBKDF2_HMAC(password.c_str(), password.length(),
                                        salt.data(), salt.size(),
                                        10000, EVP_sha256(),
                                        hashed_password.size(), hashed_password.data());

        if (result == 0) {
            // Handle error
            ERR_print_errors_fp(stderr);
            return {};
        }

        // Resize the vectors to the correct length
        hashed_password.resize(EVP_MD_size(EVP_sha256()));
        salt.resize(EVP_MD_size(EVP_sha256()));

        // Store the result
        hashed_passwords.emplace_back(std::move(hashed_password), std::move(salt));
    }

    return hashed_passwords;
}
```