#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

std::string generate_receive_log(const std::string &msg) {
    // Get current time as a time_point
    auto now = std::chrono::system_clock::now();
    // Convert to time_t for formatting
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    
    // Create a tm struct to format the time
    std::tm now_tm = *std::localtime(&now_time_t);
    
    // Create a string stream to format the timestamp
    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");
    
    // Generate the log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + msg;
    
    return log_entry;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <message>\n";
        return EXIT_FAILURE;
    }

    // Ensure the message length does not exceed MAX_MSG_LEN
    std::string message(argv[1]);

    // Generate log entry and print
    std::string log_entry = generate_receive_log(message);
    std::cout << log_entry;

    return EXIT_SUCCESS;
}
