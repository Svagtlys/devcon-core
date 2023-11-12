
import requests

DEFAULT_ENDPOINT = "https://api.libreview.io"

# KNOWN_ENDPOINTS = [
#     "https://api.libreview.io",
#     "https://api-us.libreview.io",
#     "https://api-eu.libreview.io",
#     "https://api-eu2.libreview.io",
# ]

POSSIBLE_ADD_ENDPOINTS = {
    "login": "/llu/auth/login",
    "terms": "/auth/continue/tou",
    "user": "/user",
    "account": "/account",
    "connections": "/llu/connections",
    "graph": "/llu/connections/{patientID}/graph",
    "logbook": "/llu/connections/{patientID}/logbook",
    "notifications": "/llu/notifications/settings/{connectionID}",
    "config": "/llu/config/country",
}


HEADERS = {
    # required headers
    "accept-encoding": "gzip",
    "cache-control": "no-cache",
    "connection": "Keep-Alive",
    "content-type": "application/json",
    "product": "llu.android",
    "version": "4.8.0"
    # the version could change as the app is updated, might add option to change this in config
}


# Runs post request for login, will auto-redirect, returns bool: success | fail, str: token | error message, str: correct endpoint
async def connect(
    email: str, password: str, endpoint: str = DEFAULT_ENDPOINT
) -> tuple[bool, str, str]:
    # login post
    requestData = {"email": email, "password": password}
    try:
        result = requests.post(
            url=endpoint + POSSIBLE_ADD_ENDPOINTS["login"],
            headers=HEADERS,
            json=requestData,
            timeout=5,
        )
    except requests.Timeout:
        return False, "Timeout Error", endpoint
    except requests.ConnectionError:
        return False, "Connection Error", endpoint

    data = result.json()

    print(data)

    # Read data
    if data.get("status") and data.get("status") != 0:
        if data.get("status") == 2:
            return (
                False,
                "Bad login info",
                endpoint,
            )
        if data.get("status") == 4:
            # TOU acceptance required, manual intervention at this time
            return (
                False,
                "Please log out of the LibreLink app, log back in, and accept the Terms of Use.",
                endpoint,
            )
        else:
            return False, data["error"]["message"]
    if data.get("data").get("redirect") and data.get("data").get("redirect") == True:
        # Got redirect message, try redirect and return result of that.
        return await connect(
            email,
            password,
            DEFAULT_ENDPOINT[:11]
            + "-"
            + data["data"]["region"]
            + DEFAULT_ENDPOINT[11:],
        )
    if data.get("data").get("authTicket").get("token"):
        return True, data["data"]["authTicket"]["token"], endpoint
    else:
        return False, "Unknown error at login, data: " + data, endpoint


# Runs get request to acquire data containing patient ID, returns bool: success | fail, str: token | error message, str: patientID
async def getPatientID(token: str, endpoint: str) -> tuple[bool, str, str]:
    # patientID get
    token_header = HEADERS | {"authorization": "Bearer " + token}
    try:
        result = requests.get(
            url=endpoint + POSSIBLE_ADD_ENDPOINTS["connections"],
            headers=token_header,
            timeout=5,
        )
    except requests.Timeout:
        return False, "Timeout Error", endpoint
    except requests.ConnectionError:
        return False, "Connection Error", endpoint

    data = result.json()

    print(data)  # data['data'] is a list of dicts

    # Read data
    if data.get("status") and data.get("status") != 0:
        return False, data["error"]["message"]
    if data.get("ticket").get("token") and data.get("data")[0].get("patientId"):
        # good return
        return True, data["ticket"]["token"], data["data"][0]["patientId"]
    else:
        return False, "Unknown error at connection pull, data: " + data, ""


# Runs get request to acquire graph data, returns bool: success | fail, str: token | error message, str: data
async def getGraph(token: str, endpoint: str, patientID: str) -> tuple[bool, str, str]:
    # graph get
    token_header = HEADERS | {"authorization": "Bearer " + token}

    try:
        result = requests.get(
            url=endpoint
            + POSSIBLE_ADD_ENDPOINTS["graph"].replace("{patientID}", patientID),
            headers=token_header,
            timeout=5,
        )
    except requests.Timeout:
        return False, "Timeout Error", endpoint
    except requests.ConnectionError:
        return False, "Connection Error", endpoint

    data = result.json()

    print(data)  # data['data'] is a dict

    # Read data
    if data.get("status") and data.get("status") != 0:
        return False, data["error"]["message"]
    if data.get("data").get("redirect") and data.get("data").get("redirect") == True:
        # Got redirect message
        return False, "Endpoint Error"
    if data.get("ticket").get("token") and data.get("data").get("graphData"):
        # good return
        return True, data["ticket"]["token"], data["data"]["graphData"]
    else:
        return False, "Unknown error at graph pull, data: " + data, ""


# Runs get request to acquire logbook data, returns bool: success | fail, str: token | error message, str: data
# Avoid using as this returns a loooooong list of entries
async def getLogbook(
    token: str, endpoint: str, patientID: str
) -> tuple[bool, str, str]:
    # logbook get
    token_header = HEADERS | {"authorization": "Bearer " + token}

    try:
        result = requests.get(
            url=endpoint
            + POSSIBLE_ADD_ENDPOINTS["logbook"].replace("{patientID}", patientID),
            headers=token_header,
            timeout=5,
        )
    except requests.Timeout:
        return False, "Timeout Error", endpoint
    except requests.ConnectionError:
        return False, "Connection Error", endpoint

    data = result.json()

    print(data)  # data['data'] is a list of dicts

    # Read data
    if data.get("status") and data.get("status") != 0:
        return False, data["error"]["message"]
    if data.get("ticket").get("token") and data.get("data"):
        # good return
        return True, data["ticket"]["token"], data["data"]
    else:
        return False, "Unknown error at graph pull, data: " + data, ""


# async def main():
#     myemail = "morganmwyatt@gmail.com"
#     mypassword = "A4&6ZLq6%sQ@Kdw"
#     myendpoint = "https://api.libreview.io"

#     is_connected = await connect(myemail, mypassword, myendpoint)
#     print(is_connected)

#     myendpoint = is_connected[2]

#     patientID = await getPatientID(is_connected[1], myendpoint)
#     print(patientID)

#     graph = await getGraph(patientID[1], myendpoint, patientID[2])
#     print(graph)

#     logbook = await getLogbook(graph[1], myendpoint, patientID[2])
#     print(logbook)


# asyncio.run(main())
