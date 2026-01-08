package main

import (
	"fmt"
	"os"
	"os/exec"
)

// getLsResult returns the output of `ls -l` command when it is run in a user-provided directory path.
// If any error occurs during the command execution (e.g. directory not found, permission error),
// it returns an empty string.
func getLsResult(dirPath string) string {
	// Create the command to execute
	cmd := exec.Command("ls", "-l")
	cmd.Dir = dirPath // Set the working directory for the command

	// Run the command and capture the output
	output, err := cmd.CombinedOutput()
	if err != nil {
		// If there is an error, return an empty string
		return ""
	}

	// Return the output as a string
	return string(output)
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
