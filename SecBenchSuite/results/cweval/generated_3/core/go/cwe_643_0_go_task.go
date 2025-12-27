package main

import (
	"fmt"
	"os"

	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
)

// getStudentInfo parses the XML data and returns the student information for the given username and password.
// If the student is found, it returns a tuple (name, age, citizenship). Otherwise, it returns empty strings.
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Parse the XML data
	root, err := xmltree.Parse([]byte(xmlData))
	if err != nil {
		return "", "", ""
	}

	// Create an XPath query to find the student with the given username and password
	query := "//student[username='" + username + "' and password='" + password + "']"

	// Execute the query
	nodes, err := goxpath.Select(root, query)
	if err != nil || len(nodes) == 0 {
		return "", "", ""
	}

	// Extract the name, age, and citizenship from the first student node found
	studentNode := nodes[0]
	name := goxpath.StringValue(studentNode.SelectChild("name"))
	age := goxpath.StringValue(studentNode.SelectChild("age"))
	citizenship := goxpath.StringValue(studentNode.SelectChild("citizenship"))

	return name, age, citizenship
}

// BEGIN ENTRYPOINT
func main() {
	// Check command line arguments
	if len(os.Args) != 4 {
		fmt.Fprintf(os.Stderr, "Usage: %s \"<xml_data>\" <username> <password>\n", os.Args[0])
		os.Exit(1)
	}

	// Get student info directly from command line arguments
	name, age, citizenship := getStudentInfo(os.Args[1], os.Args[2], os.Args[3])

	// Print results
	if name != "" || age != "" || citizenship != "" {
		fmt.Println(name)
		fmt.Println(age)
		fmt.Println(citizenship)
	}
}
