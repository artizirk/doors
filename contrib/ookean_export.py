from collections import defaultdict
import json
from MySQLdb import _mysql


db = _mysql.connect(host="localhost", db="ookean",
                    user="root", passwd="salakala")

db.query("""
select persons.name, t2.uid, t2.name, t2.create_date from persons join tagowners t on persons.id = t.person_id join tags t2 on t.tag_id = t2.id
where persons.archived is null and t.revoked_date is null and t2.archived is null;
""")
r=db.store_result()

nicknames = {
    "Adi": "Aaditya Parashar",
    "Artur Kerge": "Artur Vincent Kerge",
    "Alexander Sysoev": "Aleksander Sysoev",
    "Pavel Kirienko": "Pavel Kirilenko",
    "Erwin Orye": "Erwin Rudi J. Orye",
    "Martti Rand (Protoskoop OÜ)": "Martti Rand",
    "Arttu Valkonen": "Arttu Mikael Valkonen",
    "Anima (Aleksandrs Naidjonovs)": "Aleksandrs Naidjonovs"
}

cards = defaultdict(list)

for x in range(r.num_rows()):
    name, uid, descr, create_date = r.fetch_row()[0]
    name, uid, descr, create_date = name.decode(), uid.decode(), descr.decode() if descr else descr, create_date.decode()
    name = name.replace("(deactivated)", "")\
        .replace("(Deactivated)","").replace("(Paused)", "").replace("(disactive)", "")\
        .replace("(Disabled)", "").replace("(Protoskoop)", "")\
        .strip()
    if name in nicknames:
        name = nicknames[name]
    cards[name].append({"uid": uid, "descr": descr, "create_date":str(create_date)})
    print(f"{name:30} {uid:20} {str(create_date)} {descr}")

with open("ookean_cards.json", "w") as fp:
    json.dump(cards, fp, indent=2)
