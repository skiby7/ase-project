import random
import string
from locust import HttpUser, task, between
import urllib3
from time import time
unix_time = lambda: int(time())
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


adjectives = [
    "adoring", "affectionate", "agitated", "amazing", "awesome", "beautiful",
    "blissful", "bold", "brave", "busy", "charming", "clever", "cool", "crazy",
    "dazzling", "determined", "dreamy", "eager", "ecstatic", "elated", "epic",
    "exciting", "fervent", "festive", "flamboyant", "focused", "friendly",
    "frosty", "gallant", "gifted", "goofy", "gracious", "happy", "hardcore",
    "heuristic", "hopeful", "hungry", "infallible", "inspiring", "intelligent",
    "jolly", "jovial", "keen", "kind", "laughing", "loving", "magical", "mystifying",
    "naughty", "nervous", "nifty", "nostalgic", "objective", "optimistic",
    "peaceful", "pedantic", "pensive", "practical", "priceless", "quirky", "quizzical",
    "recursing", "relaxed", "reverent", "romantic", "sad", "serene", "sharp",
    "silly", "sleepy", "stoic", "stupefied", "suspicious", "sweet", "tender",
    "thirsty", "trusting", "unruffled", "vibrant", "vigilant", "vivid", "wonderful",
    "xenodochial", "youthful", "zealous", "zen"
]

names = [
    "albattani", "allen", "almeida", "archimedes", "ardinghelli", "aryabhata",
    "austin", "babbage", "banach", "bardeen", "bartik", "bassi", "bell",
    "benz", "bhabha", "bhaskara", "blackwell", "bohr", "booth", "borg",
    "bose", "boyd", "brahmagupta", "brattain", "brown", "carson", "cartwright",
    "chandrasekhar", "shannon", "clarke", "colden", "cori", "cray", "curran",
    "curie", "darwin", "davinci", "dijkstra", "dubinsky", "easley", "einstein",
    "elion", "engelbart", "euclid", "euler", "fermat", "fermi", "feynman",
    "franklin", "galileo", "gates", "goldberg", "goldstine", "goldwasser",
    "golick", "goodall", "hamilton", "hawking", "heisenberg", "hermann",
    "herschel", "hertz", "hopper", "hugle", "hypatia", "ishizaka", "jennings",
    "jones", "kalam", "kare", "keller", "kepler", "kowalevski", "lalande",
    "lamarr", "leakey", "lewin", "lichterman", "lovelace", "lumiere",
    "mahavira", "mayer", "mccarthy", "mcclintock", "mclean", "meitner",
    "mendel", "mendeleev", "mirzakhani", "moore", "napier", "nash", "neumann",
    "newton", "nightingale", "nobel", "noether", "northcutt", "pare", "pasteur",
    "payne", "perlman", "pike", "poincare", "poitras", "ptolemy", "raman",
    "ramanujan", "ride", "ritchie", "roentgen", "rosalind", "saha", "sammet",
    "shaw", "shockley", "sinoussi", "snyder", "spence", "stonebraker", "swanson",
    "tereshkova", "tesla", "thompson", "torvalds", "turing", "varahamihira",
    "visvesvaraya", "volhard", "wescoff", "wiles", "williams", "wilson",
    "wing", "wozniak", "wright", "yonath", "zhukovsky"
]

linux_distros = [
    "Alpine Linux",
    "Arch Linux",
    "Bodhi Linux",
    "Debian",
    "Fedora",
    "Gentoo",
    "HannaMontana Linux",
    "Kali Linux",
    "Manjaro",
    "Mint",
    "NixOS",
    "openSUSE",
    "Pop!_OS",
    "Raspberry Pi OS",
    "Slackware",
    "Solus",
    "Tails",
    "TempleOS",
    "Ubuntu",
    "Void Linux",
    "Zorin OS"
]

def gen_username():
    adjective = random.choice(adjectives)
    name = random.choice(names)
    return f"{adjective}_{name}_{random.randint(0, 100)}"

def gen_email(username: str):
    return f"{username}@unipi.it"

def gen_password(length: int = 12):
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%?/"

    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(symbols),
        '@'
    ]

    all_characters = uppercase + lowercase + digits + symbols
    password += random.choices(all_characters, k=length - 5)
    random.shuffle(password)
    return ''.join(password)

class Operations():
    register = "/api/auth/accounts"
    login = "/api/auth/token"
    userinfo = "/api/auth/userinfo"
    buy = "/api/tux-management/buy"
    roll = "/api/distro/{}/gacha/roll"
    system_collection = "/api/distro/user/gacha/all"
    distro_info = "/api/distro/user/gacha/{}"
    transaction_history = "/api/tux-management/transactions/{}"
    create_auction = "/api/auction/auctions"
    bid = "/api/auction/auctions/{}/bids"


class UserBehavior(HttpUser):
    wait_time = between(1, 3)  # Users wait between 1 and 3 seconds between tasks

    # Headers and initial setup
    def on_start(self):
        self.users = []
        # self.register_url = "/api/auth/accounts"
        # self.login_url = "/api/auth/token"
        # self.user_data = {
        #     "username" : "testuser",
        #     "password" : "T3stPassword@!",
        #     "email"    : "test@gmail.com"
        # }
        # self.auth_token = None
        # self.user_id = None
        # self.register()

    def fetch_token(self, user_data: dict):
        data = {
            "grant_type": "password",
            "username": user_data["username"],
            "password": user_data["password"],
        }

        response = self.client.post(
            Operations.login,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=False
        )

        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token"), token_data.get("token_type")

        print(f"Failed to fetch token: {response.status_code} {response.text}")
        return None, None

    def login(self, user_data, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = self.client.get(
            Operations.userinfo,
            data=user_data,
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("uid")
        print(f"Failed to fetch token: {response.status_code} {response.text}")
        return None

    def do_auth(self, user_data):
        auth_token, _ = self.fetch_token(user_data)
        if not auth_token:
            print("No auth token, skipping...")
            return None, None
        user_id = self.login(user_data, auth_token)

        if not user_id:
            print("No auth token, skipping...")
            return None, None
        return user_id, {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


    def buy_tux(self, user_id, headers, amount):
        data = {"user_id":str(user_id), "amount" : amount}
        response = self.client.post(
            Operations.buy,
            json=data,
            headers=headers,
            verify=False
        )

        return response


    @task(weight=20)
    def register(self):
        username = gen_username()
        user_data = {
            "username" : username,
            "password" : gen_password(),
            "email"    : gen_email(username)
        }
        response = self.client.post(
            Operations.register,
            json=user_data,
            verify=False  # Accept self-signed certificates
        )
        if response.status_code in (200, 201):
            print("Registration successful")
            self.users.append({  # type: ignore
                "username" : user_data["username"],
                "password" : user_data["password"]
            })
            print(f"{len(self.users)} available")
            return
        else:
            print(f"Failed to register: {response.status_code} {response.text}")
            return

    @task(weight=2)
    def they_see_me_rolling(self):
        if len(self.users) == 0:
            print("No users available, skipping...")
            return

        user_data = random.choice(self.users)
        if not user_data:
            return
        user_id, headers = self.do_auth(user_data)
        if not user_id or not headers:
            return
        for i in range(10):
            response = self.buy_tux(user_id, headers, 10)
            if response.status_code == 200:
                print("Operation performed successfully")
            else:
                print(f"Failed to perform operation: {response.status_code} {response.text}")
                continue

            response = self.client.post(
                Operations.roll.format(user_id),
                headers=headers,
                verify=False
            )

            if response.status_code == 200:
                print("Operation performed successfully")
            else:
                print(f"Failed to perform operation: {response.status_code} {response.text}")

    @task(weight=3)
    def get_distro_info(self):
        if len(self.users) == 0:
            print("No users available, skipping...")
            return

        user_data = random.choice(self.users)
        if not user_data:
            return
        user_id, headers = self.do_auth(user_data)
        if not user_id or not headers:
            return
        response = self.client.get(
            Operations.distro_info.format(random.choice(linux_distros)),
            headers=headers,
            verify=False
        )
        if response.status_code == 200:
            print("Operation performed successfully")
        else:
            print(f"Failed to perform operation: {response.status_code} {response.text}")

    @task(weight=3)
    def get_distro_available(self):
        if len(self.users) == 0:
            print("No users available, skipping...")
            return

        user_data = random.choice(self.users)
        if not user_data:
            return
        user_id, headers = self.do_auth(user_data)
        if not user_id or not headers:
            return
        response = self.client.get(
            Operations.system_collection,
            headers=headers,
            verify=False
        )
        if response.status_code == 200:
            print("Operation performed successfully")
        else:
            print(f"Failed to perform operation: {response.status_code} {response.text}")

    @task(weight=3)
    def get_user_transactions(self):
        if len(self.users) == 0:
            print("No users available, skipping...")
            return

        user_data = random.choice(self.users)
        if not user_data:
            return
        user_id, headers = self.do_auth(user_data)
        if not user_id or not headers:
            return
        response = self.client.get(
            Operations.transaction_history.format(user_id),
            headers=headers,
            verify=False
        )
        if response.status_code == 200:
            print("Operation performed successfully")
        else:
            print(f"Failed to perform operation: {response.status_code} {response.text}")

    @task
    def auction(self):
        if len(self.users) < 6:
            print("Not enough users to open an auction")
            return
        auction_duration = 10
        starting_price = 10
        users = random.sample(self.users, len(self.users) // 2)

        auctioneer = users[0]
        bidders = users[1:]


        user_id, headers = self.do_auth(auctioneer)
        if not user_id or not headers:
            return
        auctioneer["user_id"] = user_id
        auctioneer["headers"] = headers


        response = self.buy_tux(user_id, headers, 10)
        if response.status_code == 200:
            print("Operation performed successfully")
        else:
            print(f"Failed to perform operation: {response.status_code} {response.text}")
            return


        if response.status_code != 200:
            print(f"Failed to perform operation: {response.status_code} {response.text}")
            return

        response = self.client.post(
            Operations.roll.format(auctioneer["user_id"]),
            headers=auctioneer["headers"],
            verify=False
        )

        if response.status_code != 200:
            print(f"Failed to perform operation: {response.status_code} {response.text}")
            return

        gacha = response.json()["name"]

        for bidder in bidders:
            user_id, headers = self.do_auth(auctioneer)
            if not user_id or not headers:
                return

            bidder["user_id"] = user_id
            bidder["headers"] = headers

            response = self.buy_tux(user_id, headers, 1000)
            if response.status_code == 200:
                print("Operation performed successfully")
            else:
                print(f"Failed to perform operation: {response.status_code} {response.text}")
                continue

        start_time = unix_time()
        auction_data = {
            "player_id": f"{auctioneer["user_id"]}",
            "gacha_name": gacha,
            "starting_price": starting_price,
            "end_time": start_time + auction_duration
        }
        response = self.client.post(
            Operations.create_auction.format(auctioneer["user_id"]),
            headers=auctioneer["headers"],
            json=auction_data,
            verify=False
        )
        if response.status_code != 201:
            return
        auction_id = response.json()["auction_id"]
        last_bid = starting_price
        while unix_time() - start_time < auction_duration:
            bidder = random.choice(bidders)
            data = {"auction_id": auction_id, "player_id": bidder["user_id"], "bid" : last_bid}
            response = self.client.post(
                Operations.bid.format(auction_id),
                json=data,
                headers=auctioneer["headers"],
                verify=False
            )
            if response.status_code != 200:
                continue
            last_bid += 1
