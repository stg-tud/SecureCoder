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

We can construct a XPath query and then execute the query to search for the student information.

@param xmlData The XML data containing the student information.
@param username The username of the student to search for.
@param password The password of the student to search for.

@return A tuple (name, age, citizenship) if the student is found. Otherwise, returns empty strings.
*/
func getStudentInfo(xmlData, username, password string) (string, string, string) {
	// Parse the XML data
	reader := strings.NewReader(xmlData)
	doc, err := xmltree.Parse(reader)
	if err != nil {
		return "", "", ""
	}

	// Create an XPath query to find the student with the given username and password
	xpathExpr := "//student[username='" + username + "' and password='" + password + "']"
	nodes, err := goxpath.Select(xpathExpr, doc)
	if err != nil || len(nodes) == 0 {
		return "", "", ""
	}

	// Extract the student information
	studentNode := nodes[0]
	name := getNodeValue(studentNode, "name")
	age := getNodeValue(studentNode, "age")
	citizenship := getNodeValue(studentNode, "citizenship")

	return name, age, citizenship
}

// Helper function to get the text value of a child element by name
func getNodeValue(node tree.Node, childName string) string {
	if childNode := node.FirstChild(); childNode != nil {
		for childNode != nil {
			if childNode.(*xmltree.Element).Name.Local == childName {
				return childNode.(*xmltree.Element).Text
			}
			childNode = childNode.NextSibling()
		}
	}
	return ""
}
```