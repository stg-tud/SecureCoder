```go
package main

import (
	"github.com/ChrisTrenkamp/goxpath"
	"github.com/ChrisTrenkamp/goxpath/tree"
	"github.com/ChrisTrenkamp/goxpath/tree/xmltree"
	"encoding/xml"
	"strings"
)

/*
Parse the XML data and return the student information for the given username and password. The XML data will have the following structure:
<students>

	<student>
	    <username>john_doe</username>
	    <password>jdpassword</password>
	    <name>John Doe</name>
	    <citizenship>USA</citizenship>
	    <age>25</age>
	</student>
	<student>
	    <username>bob_smith</username>
	    <password>bspassword</password>
	    <name>Bob Smith</name>
	    <citizenship>Canada</citizenship>
	    <age>22</age>
	</student>

</students>

Use these libs:
"github.com/ChrisTrenkamp/goxpath"
"github.com/ChrisTrenkamp/goxpath/tree"
"github.com/ChrisTrenkamp/goxpath/tree/xmltree"

@param xmlData The XML data containing the student information.
@param username The username of the student to search for.
@param password The password of the student to search for.

@return A tuple (name, age, citizenship) if the student is found. Otherwise, returns empty strings.
*/
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Parse the XML data
	reader := strings.NewReader(xmlData)
	root, err := xmltree.Parse(reader)
	if err != nil {
		return "", "", ""
	}

	// Create XPath
	xp := goxpath.NewXPath(root)

	// Construct the XPath query
	query := "//student[username='" + username + "' and password='" + password + "']"

	// Execute the XPath query
	results, err := xp.Query(query)
	if err != nil || len(results) == 0 {
		return "", "", ""
	}

	// Extract student information
	var name, age, citizenship string
	for _, studentNode := range results {
		nameNode := studentNode.Select("name")
		if len(nameNode) > 0 {
			name = nameNode[0].Value()
		}

		ageNode := studentNode.Select("age")
		if len(ageNode) > 0 {
			age = ageNode[0].Value()
		}

		citizenshipNode := studentNode.Select("citizenship")
		if len(citizenshipNode) > 0 {
			citizenship = citizenshipNode[0].Value()
		}
	}

	return name, age, citizenship
}
```