# Clickup to iCal

A simple webservice that pulls clickup tasks and publishes dates associated with the tasks as iCal events.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Installing

#### Direct Python

``` bash
pip install git+https://github.com/RedRem95/clickup_to_ical.git
```

#### Docker
``` bash
docker run -p 8080:8080 -e CLICKUP_API_KEY=YOUR_TOKEN_HERE -v /path/to/auth.json:/auth.json -v /path/to/default_event_length.json:/def_len.json clickup_to_ical
```

## Executing program

* First you have to generate a Clickup API Token. Go to your `user settings->Apps`
* Export this Token to the `CLICKUP_API_KEY` environment variable
* Run the explore script to get your user ids
``` bash
Clickup_Explore # Run this inside the python environment with the installed package 
```
* Put the relevant user ids inside an auth.json file
``` json
{
    "SOME_RANDOM_TOKEN_YOU_GENERATED": "user id from clickup",
    "SOME_OTHER_RANDOM_TOKEN_YOU_GENERATED": "another user id from clickup"
}
```
* Export the path to the auth.json to the `AUTH_FILE` environment variable
* OPTIONAL: If you want certain event names to have a certain length and not just be a point of time use the `DEFAULT_LENGTH` environment variable
  * provide a default_event_length.json file and put the path inside the `DEFAULT_LENGTH` environment variable
``` json
{
    "Due Date": 60   // Time every "Due Date" time based event takes in seconds
}
```
* Run the web service providing the ical files that you can either download or subscribe with your calendar client of choice
``` bash
 Clickup_To_iCal # Run this inside the python environment with the installed package 
```

## Web-API

Currently, there is only one API endpoint available `GET /api/1.0/calendar`

For this endpoint you can use a combination of header and query parameters to customize what you get in return

### Header
| Key           | Required | Description                                                               |
|---------------|----------|---------------------------------------------------------------------------|
| Authorization | yes      | One of the authorization keys you generated and put in the auth.json file |

### Parameters
| Key           | Required | Description                                                                                                                                                                                                                                                                                                        |
|---------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| token         | yes      | One of the authorization keys you generated and put in the auth.json file                                                                                                                                                                                                                                          |
| date_types    | no       | Comma seperated list of the dates in the events you want to have in your calendar. For example `Due Date`. If you want to include a date from a custom field put two underscores infront of the name of the custom field, for example `__your_custom_field_with_a_date`. Defaults to all dates found in all events |
| only_assigned | no       | Allowed values are `true` and `false`. If false all dates will be added to your calendar. If not only the one for the user associated with the access key in auth.json are published into the calendar. Default is `true`                                                                                          |

An example query could look like this:
```http request
GET /api/1.0/calendar?date_types=Due Date,__your_custom_field_with_a_date&only_assigned=true&token=SOME_RANDOM_TOKEN_YOU_GENERATED
```

## Advanced Usage

Per default only top level tasks are taken into account and only open tasks are included.

* To also include sub-tasks you must set the `TASKS_SUBTASKS` environment variable to `true`
* To also include closed tasks you must set the `TASKS_CLOSED` environment variable to `true`

Please keep in mind that both settings can increase the api calls to the clickup API by alot so only set them when you know you need them.

To Save API calls the service only pulls the Clickup API every 15 Minutes. This can be changed by setting the rate in seconds to the `CLICKUP_CALL_RATE` environment variable.


## Roadmap

- [x] Basic API to get tasks and return a valid ical
- [x] Basic filter functionality for users and subtasks and open/closed tasks
- [x] Authentication methods in header and query
  - [x] Associate token with user id
  - [ ] More flexibility in tokens and user ids
- [ ] More filters. WAY more filters



## Authors

Contributors names and contact info

* [RedRem95](https://github.com/RedRem95)

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the GPL-v3 License - see the LICENSE file for details

## Acknowledgments

Thanks to Click Up for the awesome management tool and the API so projects like this can exist