```js
/*
storeInfoInHeader stores the provided information in an existing HTTP response header object under the specified type.
This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
Information content is read from user requests.
If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header map without any changes.

@param {string} infoType The type of information to store in the header.
@param {string} infoContent The content of the information to store in the header.
@param {object} header The existing response header map.
@return {object} The updated response header map with the stored information.
*/
function storeInfoInHeader(infoType, infoContent, header) {
    // Check if the header object is valid
    if (typeof header !== 'object' || header === null) {
        return header; // return original header if invalid
    }

    // Define the mapping of infoType to header keys
    const headerKeys = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Check if the provided infoType is valid
    if (headerKeys.hasOwnProperty(infoType)) {
        // Store the infoContent in the appropriate header key
        header[headerKeys[infoType]] = infoContent;
        return header; // return updated header
    }

    // If infoType is not valid, return the original header
    return header;
}
```