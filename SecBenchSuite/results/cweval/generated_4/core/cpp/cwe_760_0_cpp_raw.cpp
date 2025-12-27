```cpp
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <string>
#include <utility>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    // Ensure the count does not exceed the size of usernames and passwords
    if (count > usernames.size() || count > passwords.size()) {
        return hashed_passwords; // Return empty vector if count is invalid
    }

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];
        
        // Generate a random salt of length equal to the hash output
        std::vector<unsigned char> salt(EVP_MAX_MD_SIZE);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            ERR_print_errors_fp(stderr);
            return hashed_passwords; // Return empty if salt generation fails
        }

        // Prepare to hash the password
        std::vector<unsigned char> hashed_password(EVP_MD_size(EVP_sha256()));
        if (!PKCS5_PBKDF2_HMAC(password.c_str(), password.length(), salt.data(), salt.size(), 10000, EVP_sha256(), hashed_password.size(), hashed_password.data())) {
            ERR_print_errors_fp(stderr);
            return hashed_passwords; // Return empty if hashing fails
        }

        // Store the hashed password and the corresponding salt
        hashed_passwords.emplace_back(std::make_pair(hashed_password, salt));
    }

    return hashed_passwords;
}
```