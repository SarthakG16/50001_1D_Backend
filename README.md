# Registering, Logging In, Logging Out

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

# Posters

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
