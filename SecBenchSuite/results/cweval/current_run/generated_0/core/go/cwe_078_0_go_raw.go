```go
package main

import (
	"bytes"
	"os/exec"
	"path/filepath"
)

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
func getLsResult(dirPath string) string {
	// Validate the provided directory path
	if dirPath == "" {
		return ""
	}

	// Ensure the path is a valid directory
	if _, err := filepath.Abs(dirPath); err != nil {
		return ""
	}

	// Prepare the command
	cmd := exec.Command("ls", "-l", dirPath)

	// Capture the output
	var out bytes.Buffer
	cmd.Stdout = &out

	// Run the command
	if err := cmd.Run(); err != nil {
		return ""
	}

	// Return the output as a string
	return out.String()
}
```