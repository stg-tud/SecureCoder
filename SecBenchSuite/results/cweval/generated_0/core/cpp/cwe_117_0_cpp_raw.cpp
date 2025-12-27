```cpp
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

std::string generate_receive_log(const std::string &msg) {
    // Get the current time as a time point
    auto now = std::chrono::system_clock::now();
    
    // Convert to time_t to get the calendar time
    auto now_c = std::chrono::system_clock::to_time_t(now);
    
    // Convert to tm structure for formatting
    std::tm now_tm = *std::localtime(&now_c);

    // Create a string stream for the ISO format
    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");

    // Create the log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + msg;

    return log_entry;
}
```