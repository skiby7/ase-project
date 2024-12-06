import requests
import pandas as pd
import matplotlib.pyplot as plt

#1000 circa 1200
# comprare i tux

#100 roll

USER = 100 # 100 rolls each

distros = [
    {"name": "Ubuntu", "rarity": "1"},
    {"name": "Debian", "rarity": "1"},
    {"name": "Fedora", "rarity": "1"},
    {"name": "Arch Linux", "rarity": "2"},
    {"name": "openSUSE", "rarity": "2"}, 
    {"name": "Mint", "rarity": "1"},
    {"name": "Manjaro", "rarity": "2"},
    {"name": "HannaMontana Linux", "rarity": "5"},
    {"name": "Gentoo", "rarity": "3"},
    {"name": "Raspberry Pi OS", "rarity": "1"},
    {"name": "TempleOS", "rarity": "5"},
    {"name": "Slackware", "rarity": "4"},
    {"name": "Alpine Linux", "rarity": "3"},
    {"name": "Tails", "rarity": "4"},
    {"name": "Kali Linux", "rarity": "1"},
    {"name": "Pop!_OS", "rarity": "2"},
    {"name": "Zorin OS", "rarity": "2"},
    {"name": "Bodhi Linux", "rarity": "4"},
    {"name": "Solus", "rarity": "4"},
    {"name": "NixOS", "rarity": "4"},
    {"name": "Void Linux", "rarity": "4"}
]

def data_creation(n: str):
    data = {
            "username" : f"pippo{n}",
            "password" : f"Pippo{n}13579@",
            "email"    : f"pippo{n}@pippomail.com"
        }
    return data
        
def register(data):
        response = requests.post("https://127.0.0.1:8080/api/auth/accounts", json=data, verify=False)

        if response.status_code in (200, 201):
            print("Registration successful")
            print(f"{data["username"]} available")
            return
        else:
            print(f"Failed to register: {response.status_code} {response.text}")
            return

def login(data):
    response = requests.post("https://127.0.0.1:8080/api/auth/token", data=data,headers={"Content-Type": "application/x-www-form-urlencoded"}, verify=False)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")

    print(f"Failed to fetch token: {response.status_code} {response.text}")
    return None

def userinfo(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://127.0.0.1:8080/api/auth/userinfo", data=data, headers=headers, verify=False)

    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("uid")
    print(f"Failed to fetch token: {response.status_code} {response.text}")

def buy(id, token):
    data = {"user_id":str(id), "amount" : 1200}
    headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    response = requests.post("https://127.0.0.1:8080/api/tux-management/buy", json=data, headers=headers, verify=False)

    if response.status_code == 200:
        print("Operation performed successfully")
    else:
        print(f"Failed to perform operation: {response.status_code} {response.text}")

def roll(id, token):
    headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    response = requests.post(f"https://127.0.0.1:8080/api/distro/{id}/gacha/roll",headers=headers, verify=False)

    if response.status_code == 200:
        print("Operation performed successfully")
        gacha = response.json()
        return gacha["name"]
    else:
        print(f"Failed to perform operation: {response.status_code} {response.text}")

gachas_name=[]

for n in range(1, USER):
    data=data_creation(n)
    register(data)
    token=login(data)
    uid=userinfo(data,token)
    buy(uid,token)
    for i in range(1, 100):
        gachas_name.append(roll(uid,token))

index = {item["name"]: item for item in distros}

rarities = [] 
for gacha in gachas_name:
    rarities.append(index.get(gacha)["rarity"])

rarities_series = pd.Series(rarities, name="rarities")

rarities_count = rarities_series.value_counts().sort_index()

fig, ax = plt.subplots(figsize=(19.2, 10.8))
rarities_count.plot.bar(
    ax=ax,
    color="#87CEEB",
    edgecolor="black"
)

plt.title(f"Distribution of the Rarities: {USER*100} samples", fontsize=24, fontweight='bold')
plt.xlabel("Rarity", fontsize=18, fontweight='bold')
plt.ylabel("Count", fontsize=18, fontweight='bold')
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.7)

#plt.tight_layout()
plt.savefig(f"graph{USER*100}.png",dpi=100)