import requests

url = "https://rota.praetorian.com/rota/service/play.php"
sesskey = ""


def place(num):
    print(f"placing x at {num}")
    return under_the_hood(f"?request=place&location={num}")

def move(start, end):
    print(f"moving {start} to {end}")
    return under_the_hood(f"?request=move&from={start}&to={end}")

def status():
    return under_the_hood("?request=status")

def new():
    return under_the_hood(f"?request=new&email=aedan.e.taylor@gmail.com")

def next():
    return under_the_hood(f"?request=next")

def under_the_hood(rest_of_the_request):
    global sesskey
    result = requests.get(url + rest_of_the_request, cookies={"PHPSESSID":sesskey}) if sesskey != "" else requests.get(url + rest_of_the_request)
    # print(result.text)
    if str(result.cookies) != "<RequestsCookieJar[]>":
        sesskey = str(result.cookies).split("PHPSESSID=")[1].split(" ")[0]
    return result
