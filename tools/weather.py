from requests import get, Response
from dotenv import load_dotenv
from os import environ
from geopy.geocoders import Nominatim

from registry import register_tool

TOOL_USE_MESSAGE = "A tool for fetching condensed weather information to be displayed on an LCD \nArgs: location: str \nReturns a list of strings, each representing a page of information for the LCD."

MET_OFFICE_API_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0"

GET_HOURLY_ENDPOINT = "/point/hourly"

SAVED_LOCATIONS = {
    'home': (51.412472, -0.079944)
}


def validate_weather_args(args: list[str]) -> str:
    "For validating the args being passed to the weather tool. "
    "Returns error message string if invalid, or an empty string if valid"
    if len(args) < 1:
        return "Too few arguments.\n"

    if not type(args[0]) == str:
        return "Location must be a string."

    return ""


def validate_env_variables(env_vars: dict, *required_vars: list[str]) -> None:
    """ Validates that the requires env variables exist, otherwise throws an error with a list of the non-existent vars. """
    non_existent_vars = []

    for var in required_vars:
        if var not in env_vars:
            non_existent_vars.append(var)

    if non_existent_vars:
        raise RuntimeError(
            f"Missing Environment Variables: {non_existent_vars}")


def get_lat_long_from_string(location_string: str, user_agent: str) -> tuple:
    """Takes a string location, and returns a tuple containing the lat long of the location"""
    # Checks to see if the location in saved locations list
    saved_location = SAVED_LOCATIONS.get(location_string.lower())
    if saved_location:
        return saved_location

    # Uses Nominatim through geopy to fuzzy search for the lat long
    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.geocode(location_string)

    print(location)

    latlong = (location.latitude, location.longitude)

    print(latlong)

    return latlong


def get_met_office_response(url: str, api_key: str) -> Response:
    """ Makes the get request to the api and returns the response."""
    headers = {'apikey': api_key}

    print("Getting: ", url)

    response = get(url, headers=headers)

    return response


@register_tool("weather", TOOL_USE_MESSAGE)
def weather(*args: list[str]) -> list[str]:

    # Validates the args for the weather tool
    invalidation = validate_weather_args(args)
    if invalidation:
        return [f"Error: {invalidation}" + TOOL_USE_MESSAGE]

    # Sets up and validates environment variables
    load_dotenv()
    validate_env_variables(environ, "MET_OFFICE_API_KEY", "OSM_USER_AGENT")
    MET_OFFICE_API_KEY = environ["MET_OFFICE_API_KEY"]
    OSM_USER_AGENT = environ["OSM_USER_AGENT"]

    # Gets the lat long for the weather request
    lat_long = get_lat_long_from_string(args[0], OSM_USER_AGENT)

    hourly_ulr = MET_OFFICE_API_URL + GET_HOURLY_ENDPOINT
    response = get_met_office_response(
        hourly_ulr, lat_long, MET_OFFICE_API_KEY)

    print(response.json())


if __name__ == "__main__":
    weather('spain barcelona')
