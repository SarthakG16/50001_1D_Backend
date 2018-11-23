# Using the Server (Mac / Linux)

Creating a database:
```bash
. venv/bin/activate
flask init-db
```
Running the server using waitress:
```bash
pip install waitress
waitress-serve --call 'actual:create_app'
```

# Using the API (NodeJS)

First, run the following command to install the 'request' module.
```
npm install request
```

```javascript
// Place this at the top of the script.
const request = require('request');

// The resulting array of dictionaries are stored in 'body'.
const request = require('request');
const fs = require('fs');

request("http://fishy.asuscomm.com:5000/posters/", { json: true }, (err, res, body) => {
  if (err) { return console.log(err); }

  for (let i = 0; i < body.length; i++) {
    // Pull out the serialized image data, and filename.
    serialized_image_data = body[i].serialized_image_data;
    fileName = `out${i}.pdf`;

    // Write the serialized data to a pdf file.
    console.log(`Writing to ${fileName}`);
    fs.writeFile(fileName, serialized_image_data, 'base64', (err) => {
      if (err) console.log(err)
    });

  }

});


```

# Using the API (General)

Currently, the server is residing in `http://fishy.asuscomm.com:5000`, so for the commands below, add it to the end of this URL.

For example, for retrieving all poster data, use `http://fishy.asuscomm.com:5000/posters/`.

## Registering, Logging In, Logging Out

### POST /auth/register

Example input JSON:
```json
{
	"username" : "admin10",
	"password" : "password1",
	"privelage" : "administrator"
}
```
Example output JSON:
```json
{
    "status": "success"
}
```

### POST /auth/login

Example input JSON:
```json
{
	"username" : "user1",
	"password" : "hahaha",
	"requested_privelage" : "user"
}
```
Example output JSON:
```json
{
    "privelage": 0,
    "status": "success"
}
```
### GET /auth/logout
Example output JSON:
```json
{
    "status": "success"
}
```

## Posters

### GET /posters/

When logged in as a user or not logged in, a call to GET /posters/ will return all posters **with the 'posted' status**.
```json
[
  {
    "id" : 1,
    "title" : "HungrySia",
    "status" : "posted",

    "serialized_image_data" : "09uh138ehr138uhr19u3h0r312r",
    "description" : "HungrySia privides SUTD students meals during ... ",
    "category" : "mealtime",
    "locations" : "2,5",

    "contact_name" : "Andre",
    "contact_email" : "andre@hungrysia.com",
    "contact_number" : "8420 1234",
  }
]
```

When logged in as an administrator, the GET /posters/ function returns a JSON list with **every** poster.
```json
[
  {
    "id" : 1,
    "title" : "HungrySia",
    "status" : "posted",

    "serialized_image_data" : "09uh138ehr138uhr19u3h0r312r",
    "description" : "HungrySia privides SUTD students meals during ... ",
    "category" : "mealtime",
    "locations" : "2,5",

    "contact_name" : "Andre",
    "contact_email" : "andre@hungrysia.com",
    "contact_number" : "8420 1234",

    "date_submitted" : "2018-10-26 03:20:59",

    "notes_to_admin" : "Please post this we need it up urgently."
  }, {
    "id" : 2,
    "title" : "Pippip",
    "status" : "pending",

    "contact_name" : "Andre",
    "contact_email" : "andre@pippip.com",
    "contact_number" : "8420 1234",

    "date_submitted" : "2018-10-26 03:20:59",
  }
]
```
This command has a few optional parameters to refine the query performed on the server.

- `/posters/?id=2` A poster of a specific id can be requested using this parameter.


- `/posters/?status=pending` Posters with a specific status can be requested using this parameter.

- `/posters/?ignore_image=1` - Since the serialized image data can be quite large, this parameter returns results without the image data when set to 1.

### GET /posters/mine
When logged in as a user (or administrator), this command returns the poster details of the posters uploaded by the current user.

### POST /posters/
When an 'id' key is not given in the JSON request, a new poster is created, and information stored in that new poster. When creating a new poster, **the 'title' field is compulsory**.

*This command is only available when logged in as an administrator.*
```json
{
  "title" : "HungrySia",
  "status" : "pending",

  "serialized_image_data" : "09uh138ehr138uhr19u3h0r312r",
  "description" : "HungrySia privides SUTD students meals during ... ",
  "category" : "mealtime",
  "locations" : "2,5",

  "contact_name" : "Andre",
  "contact_email" : "andre@hungrysia.com",
  "contact_number" : "8420 1234",

  "date_submitted" : "2018-10-26 03:20:59",
  "date_posted" : null,
  "date_expiry" : null,

  "notes_to_admin" : "Please post this we need it up urgently."
}
```

When an 'id' key is given in the JSON request, the fields given will be updated according to the values passed in those fields.

The following JSON will update the poster with id 2.
```json
{
  "id" : 2,
  "status" : "posted",
  "date_posted" : "2018-10-26 06:20:59",
}
```

### DELETE /posters/

Deletes the poster at the given id. E.g. `DELETE /posters/?id=2` deletes the poster with id 2.

*This command is only available when logged in as an administrator.*

## Miscellaneous

### GET /current

This function returns the current user id, and their privilege.

```json
{
  "privelage": null,
  "user_id": null
}
```
