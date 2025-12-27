package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// getLsResult returns the output of the `ls -l` command when run in the provided directory path.
// If any error occurs during the command execution (e.g., directory not found, permission error),
// an empty string is returned.
func getLsResult(dirPath string) string {
	cmd := exec.Command("ls", "-l")
	cmd.Dir = dirPath

	output, err := cmd.Output()
	if err != nil {
		return ""
	}

	return strings.TrimSpace(string(output))
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there is exactly one command-line argument
	if len(os.Args) != 2 {
		return
	}

	// Get the output of the `ls -l` command
	output := getLsResult(os.Args[1])
	// Print the output
	fmt.Print(output)
}
