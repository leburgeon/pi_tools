from requests import get, Response
from dotenv import load_dotenv
from os import environ

from registry import register_tool

TOOL_USE_MESSAGE =

MET_OFFICE_API_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0"

GET_HOURLY_ENDPOINT = "/point/hourly"

SAVED_LOCATIONS = {
    'home': [51.412472, -0.079944]
}


def validate_env_variables(env_vars: dict, *required_vars: list[str]) -> None:
    """ Validates that the requires env variables exist, otherwise throws an error with a list of the non-existent vars. """
    non_existent_vars = []

    for var in required_vars:
        if var not in env_vars:
            non_existent_vars.append(var)

    if non_existent_vars:
        raise RuntimeError(
            f"Missing Environment Variables: {non_existent_vars}")


def get_met_office_weather_response(url: str, api_key: str) -> Response:
    """ Makes the get request to the api and returns the response."""
    headers = {'apikey': api_key}

    print("Getting: ", url)

    response = get(url, headers=headers)

    return response


def validate_weather_args(args: list[str]) -> str


@register_tool("weather", "Returns the weather at the location of your IP")
def weather(*args: list[str]) -> list[str]:

    if not args

    load_dotenv()
    validate_env_variables(environ, "MET_OFFICE_API_KEY")
    MET_OFFICE_API_KEY = environ["MET_OFFICE_API_KEY"]

    weather_location = get_lat_long(arf)

    hourly_ulr = MET_OFFICE_API_URL + GET_HOURLY_ENDPOINT
    response = get_met_office_weather_response(hourly_ulr, MET_OFFICE_API_KEY)

    print(response.json())


if __name__ == "__main__":
    weather()
