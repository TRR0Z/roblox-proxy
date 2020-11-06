from bs4 import BeautifulSoup

def create_gameserver(session, pid):
    resp = session.request(
        "GET", f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&placeId={pid}&isPlayTogetherGame=false")
    return resp.text

def create_game(session, name):
    rvt = BeautifulSoup(session.request(
        "GET", "https://www.roblox.com/places/create/").data, "html.parser") \
        .find("input", {"name": "__RequestVerificationToken"}).get("value")
    resp = session.request(
        "POST", "https://www.roblox.com/places/create/",
        data={
            "__RequestVerificationToken": rvt,
            "Name": name,
            "TemplateID": "95206881"
        }
    )
    if resp.status!=302: raise Exception("Failed to create new game")
    soup = BeautifulSoup(session.request("GET", "https://www.roblox.com/develop?Page=universes&close=1").text,
                         "html.parser")
    pid = soup.find(None, {"class": "start-place-url"}).get("href").split("games/")[1].split("/")[0]
    return pid

def upload_game(session, pid, data):
    resp = session.request(
        "POST", f"https://data.roblox.com/Data/Upload.ashx?assetid={pid}",
        data=data, headers={"content-type": "text/xml"})
    return resp.text.decode("UTF-8")
