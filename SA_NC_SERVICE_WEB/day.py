import sqlite3, os, time, datetime

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

print("Total Reset Process [ DAY ]")

while True:
    time.sleep(86400)
    data_list = os.listdir("./database/")
    for data in data_list:
        try:
            con = sqlite3.connect("database/" + data)
            cur = con.cursor()
            cur.execute("UPDATE info SET day = ?", (0,))
            con.commit()
            con.close()
            print(f"Success Reset [ DAY ] | {nowstr()}")
        except:
            print("Error")