```cpp
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

std::string generate_receive_log(const std::string &msg) {
    // Get the current time as a time_point
    auto now = std::chrono::system_clock::now();
    
    // Convert time_point to time_t for formatting
    std::chrono::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    
    // Convert to local time
    std::tm now_tm = *std::localtime(&now_time_t);
    
    // Create a stringstream to format the timestamp in ISO format
    std::ostringstream oss;
    oss << std::put_time(&now_tm, "%Y-%m-%dT%H:%M:%S");
    
    // Generate the log entry
    std::string log_entry = "[" + oss.str() + "] Received: " + msg;
    
    return log_entry;
}
```