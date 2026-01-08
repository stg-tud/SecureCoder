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
    if (typeof infoType !== 'string' || typeof infoContent !== 'string' || typeof header !== 'object' || header === null) {
        return header; // Return original header if inputs are invalid
    }

    switch (infoType) {
        case 'lang':
            header['Accept-Language'] = infoContent;
            break;
        case 'encoding':
            header['Accept-Encoding'] = infoContent;
            break;
        case 'cache':
            header['Cache-Control'] = infoContent;
            break;
        default:
            return header; // Return original header if infoType is not valid
    }

    return header; // Return the updated header
}
```