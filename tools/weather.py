from requests import get, Response
from dotenv import load_dotenv
from os import environ
from geopy.geocoders import Nominatim
from pprint import pp
from datetime import datetime
from zoneinfo import ZoneInfo

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

# -- Timezone --

UK_TZ = ZoneInfo('Europe/London')


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


def generate_error_message(error: str):
    """ For generating an error message including the tool use, and returning as a list of string to be displayed by the LCD"""
    return [f"Error: {error}" + TOOL_USE_MESSAGE]


def format_hourly_weather_response(weather_response: dict) -> list[str]:
    """ For formatting the weather response slides. Includes an info page on the first page"""
    response_slides = []

    try:
        location = weather_response['features'][0]['properties']['location']['name']
        if not type(location) == str:
            return generate_error_message("Weather attribute location not a string")
    except AttributeError:
        return generate_error_message("Weather attribute location did not exist")

    response_slides.append(format_weather_info_page(location, HOURLY))

    for hourly in weather_response['features'][0]['properties']['timeSeries']:
        response_slides.append(format_time_point_hourly(hourly))

    return response_slides


def format_time_point_hourly(weather_data: dict) -> str:
    """ For formatting a single weather data point for the hourly frequency.
    Weather data needs the attributes:
    {
        time: isoformat
        screenTemperature: float -> Temp in C
        feelsLikeTemperature: float -> feels like temp in C
        significantWeatherCode: int -> for description
        precipitationRate: int -> mm/h
        probOfPrecipitation: int -> % probability of precipitation
    }
    Hourly slides are returned as:
       00/00 00:00 00C (date time feels-like temp(c))
       000% 00.00mm @@ (chance-precip precip mm chars)
    """
    try:

        point_time = datetime.fromisoformat(
            weather_data['time']).astimezone(UK_TZ)
        point_temp_feels_like = weather_data['feelsLikeTemperature']
        chance_precip = weather_data['probOfPrecipitation']
        precip_rate = weather_data['precipitationRate']
    except AttributeError as e:
        return generate_error_message(f"Weather time point did not have attribute {e}")

    date = point_time.strftime('%d/%m')
    time = point_time.strftime('%H:%M')
    point_temp_feels_like = round(float(point_temp_feels_like))
    first_line = f"{date} {time} {point_temp_feels_like}C".ljust(
        LCD_LINE_LENGTH, " ")

    chance_precip = str(chance_precip).rjust(3, '0')
    precip_rate = f"{float(precip_rate):05.2f}"
    second_line = f"{chance_precip}% {precip_rate}mm @@".ljust(16, " ")

    return first_line + second_line


def format_weather_info_page(location: str, freq: str) -> str:
    """ Formats the info page for the LCD """
    first_line = f"Weather({freq})"
    first_line += " " * (LCD_LINE_LENGTH - len(first_line))
    return first_line + f"Loc: {location}"


@register_tool("weather", TOOL_USE_MESSAGE)
def weather(*args: list[str]) -> list[str]:

    return ['Weather(Hourly) Loc: Crystal Palace National Sports Centre',
            '23/07 18:00 26C 005% 00.00mm @@ ',
            '23/07 19:00 25C 005% 00.00mm @@ ',
            '23/07 20:00 22C 004% 00.00mm @@ ',
            '23/07 21:00 21C 005% 00.00mm @@ ',
            'A single page which goes too farrrr off the end? and then what? We go to the end of different screens?']

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

    return format_hourly_weather_response(response.json())


if __name__ == "__main__":
    pp(weather('home'))
