from requests import get, Response
from dotenv import load_dotenv
from os import environ
from geopy.geocoders import Nominatim
from pprint import pp

from registry import register_tool

TOOL_USE_MESSAGE = "A tool for fetching condensed weather information to be displayed on an LCD \nArgs: location: str \nReturns a list of strings, each representing a page of information for the LCD."

MET_OFFICE_API_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0"

GET_HOURLY_ENDPOINT = "/point/hourly"

SAVED_LOCATIONS = {
    'home': (51.412472, -0.079944)
}

# --- Weather Frequencies ---

HOURLY = "Hourly"

DAILY = "Daily"

# --- LCD Data ---

LCD_LINE_LENGTH = 16
LCD_NUM_LINES = 2

# --- Weather code info ---

WEATHER_CODES = {
    "NA": "Not available",
    -1: "Trace rain",
    0: "Clear night",
    1: "Sunny day",
    2: "Part cloudy",
    3: "Part cloudy",
    4: "Not used",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Light shower",
    10: "Light shower",
    11: "Drizzle",
    12: "Light rain",
    13: "Heavy shower",
    14: "Heavy shower",
    15: "Heavy rain",
    16: "Sleet shower",
    17: "Sleet shower",
    18: "Sleet",
    19: "Hail shower",
    20: "Hail shower",
    21: "Hail",
    22: "Light snow shower",
    23: "Light snow shower",
    24: "Light snow",
    25: "Heavy snow shower",
    26: "Heavy snow shower",
    27: "Heavy snow",
    28: "Thunder shower",
    29: "Thunder shower",
    30: "Thunder"
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

    try:
        return (location.latitude, location.longitude)
    except AttributeError:
        return ()


def get_met_office_response(url: str, api_key: str, lat_long: tuple) -> Response:
    """ Makes the get request to the api and returns the response."""
    headers = {'apikey': api_key}

    payload = {
        'latitude': lat_long[0],
        'longitude': lat_long[1],
        'excludeParameterMetadata': True,
        'includeLocationName': True
    }

    print("Getting: ", url)

    response = get(url, headers=headers, params=payload)

    return response


def construct_met_office_url(base_url: str, endpoint: str, latlong: tuple) -> str:
    """For constructing a url for requesting weather from the met office using lat long"""
    return


def generate_error_message(error: str):
    """ For generating an error message including the tool use, and returning as a list of string to be displayed by the LCD"""
    return [f"Error: {error}" + TOOL_USE_MESSAGE]


def format_weather_response_by_freq(weather_response: dict, freq: str) -> list[str]:
    """ For formatting the weather response slides. Includes an info page on the first page"""
    response_slides = []

    try:
        location = weather_response['features'][0]['properties']['location']['name']
        if not type(location) == str:
            return generate_error_message("Weather attribute location not a string")
    except AttributeError:
        return generate_error_message("Weather attribute location did not exist")

    response_slides.append(format_weather_info_page(location, freq))

    return response_slides

# 00/00 00:00 00C
 #   6.  12.
#


def format_time_point_hourly(weather_data: dict) -> str:
    """ For formatting a single weather data point for the hourly frequency.
    Weather data needs the attributes:
    {
        time: isoformat
        screenTemperature: float -> Temp in C
        feelsLikeTemp: float -> feels like temp in C
        significantWeatherCode: int -> for description
        precipitationRate: int -> mm/h
        probOfPrecipitation: int -> % probability of precipitation
    }"""


def format_weather_info_page(location: str, freq: str) -> str:
    """ Formats the info page for the LCD """
    first_line = f"Weather({freq})"
    first_line += " " * (LCD_LINE_LENGTH - len(first_line))
    return first_line + f"Loc: {location}"


@register_tool("weather", TOOL_USE_MESSAGE)
def weather(*args: list[str]) -> list[str]:

    # Validates the args for the weather tool
    invalidation = validate_weather_args(args)
    if invalidation:
        return generate_error_message(invalidation)

    # Sets up and validates environment variables
    load_dotenv()
    validate_env_variables(environ, "MET_OFFICE_API_KEY", "OSM_USER_AGENT")
    MET_OFFICE_API_KEY = environ["MET_OFFICE_API_KEY"]
    OSM_USER_AGENT = environ["OSM_USER_AGENT"]

    # Gets the lat long for the weather request, returning the error message if not found
    lat_long = get_lat_long_from_string(args[0], OSM_USER_AGENT)
    print(lat_long)
    if not lat_long:
        return generate_error_message(f"Location: {args[0]} not found")

    # Makes the API call
    response = get_met_office_response(
        MET_OFFICE_API_URL + GET_HOURLY_ENDPOINT, MET_OFFICE_API_KEY, lat_long)
    if not response.status_code == 200:
        return generate_error_message(f'Error fetching weather response: \nCode:{response.status_code}\nMessage:{response.json()}')

    return format_weather_response_by_frequency(response.json(), 'daily')


if __name__ == "__main__":
    pp(weather('bermondsey'))
