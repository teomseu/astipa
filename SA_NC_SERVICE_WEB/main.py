from flask import Flask, render_template, request, make_response
from flask import session, redirect, url_for, abort, jsonify
from datetime import timedelta
import datetime
import time
import sqlite3
import randomstring
import os, json
import datetime
from datetime import timedelta
import ssl
import hashlib
import random
import ast
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import threading
import vonage
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#life source edit by sia  
#Trash Source

panel_keypair = panel_keypair = {"아이디" : "비밀번호"}

app = Flask(__name__)
app.config['SERVER_NAME'] = '도메인'

cwdir =  os.path.dirname(__file__) + "/"

app.secret_key = randomstring.pick(30)

@app.template_filter('lenjago')
def lenjago(jago, txt):
    return len(jago.split(txt))

app.jinja_env.filters['lenjago'] = lenjago

if (os.path.isfile(f"{cwdir}ban.db")):
    pass
else:
    con = sqlite3.connect(f"{cwdir}ban.db")
    with con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE "ban" ("ip" TEXT);""")
        con.commit()
    con.close

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True


def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간"
    else:
        return False


def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR


def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR


def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def db(name):
    return cwdir + "database/" + name + ".db"

def hash(string):
    return str(hashlib.sha512((string + "saltysalt!@#%!@$!").encode()).hexdigest())

def search_user(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

def get_info(name):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM info;")
    result = cur.fetchone()
    con.close()
    return result

def search_prod(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM products WHERE id == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

def search_link(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM links WHERE id == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

def search_ctg(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM category WHERE id == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

def search_redeem(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM redeem WHERE code == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

def getip():
    return request.headers.get("CF-Connecting-IP", request.remote_addr)

def get_prod(name, id):
    con = sqlite3.connect(db(name))
    cur = con.cursor()
    cur.execute("SELECT * FROM products WHERE id == ?", (id,))
    result = cur.fetchone()
    con.close()
    return result

@app.route("/", methods=["GET", "POST"])
def create():
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            return render_template("create.html")
        else:
            if ("g-recaptcha-response" in request.form):
                if ("url" in request.form and "name" in request.form and "adminid" in request.form and "adminpw" in request.form and "adminpwcheck" in request.form and request.form["adminpw"] == request.form["adminpwcheck"] and "license" in request.form):
                    if (len(request.form["adminid"]) >= 6 and len(request.form["adminid"]) <= 24 and len(request.form["adminpw"]) >= 6 and len(request.form["adminpw"]) <= 24 and len(request.form["name"]) >= 1 and len(request.form["name"]) <= 12 and request.form["name"] and len(request.form["url"]) >= 3 and len(request.form["url"]) <= 12):
                        if not (os.path.isfile(db(request.form["url"]))):
                            captcha_secret = "시아는 참지않긔"
                            captcha_result = requests.get("https://www.google.com/recaptcha/api/siteverify?secret=" + captcha_secret + "&response=" + request.form["g-recaptcha-response"] + "&remoteip=" + getip()).json()
                            if (captcha_result["success"] == True):
                                con = sqlite3.connect(cwdir + "license.db")
                                with con:
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM license WHERE code == ?;", (request.form["license"],))
                                    license_result = cur.fetchone()
                                    if (license_result != None):
                                        if (license_result[2] == ""):
                                            cur.execute("UPDATE license SET usedat = ?, usedip = ?, usedurl = ? WHERE code == ?;", (nowstr(), getip(), request.form["url"], request.form["license"]))
                                            con.commit()
                                con.close()
                                if (license_result == None):
                                    return "존재하지 않는 라이센스입니다."
                                if (license_result[2] != ""):
                                    return "이미 사용된 라이센스입니다."
                                con = sqlite3.connect(db(request.form["url"]))
                                with con:
                                    cur = con.cursor()
                                    cur.execute("""CREATE TABLE "info" ("name" TEXT, "webhk" TEXT, "cultureid" TEXT, "culturepw" TEXT, "buylog" TEXT, "chargelog" TEXT, "banned" TEXT, "expiredate" TEXT, "music" TEXT, "announcement" TEXT, "fee" INTEGER, "bankaddr" TEXT, "bankpw" TEXT, "type" INTEGER, "linking" TEXT, "background" TEXT, "file" TEXT, "imgannouncement" TEXT, "buylogwebhkt" TEXT, "adminlogwebhk" TEXT, "addstock" TEXT, "channeltok" TEXT, "bankmax" TEXT, "sms" INTEGER, "nobuyer" INTEGER, "buyer" INTEGER, "vipoff" INTEGER, "vvipoff" INTEGER, "reselloff" INTEGER, "autovip" INTEGER, "autovvip" INTEGER, "autoresell" INTEGER, "bankm" INTEGER, "mm" INTEGER, "totalm" INTEGER, "nbuyerfee" INTEGER, "buyerfee" INTEGER, "vipfee" INTEGER, "vvipfee" INTEGER, "rsellfee" INTEGER, "nbuyevt" INTEGER, "buyevt" INTEGER, "vipevt" INTEGER, "vvipevt" INTEGER, "rsellevt" INTEGER, "whname" TEXT, "whimg" TEXT, "day" INTEGER, "week" INTEGER, "month" INTEGER, "keeplogincookie"  TEXT, "cash" INTEGER);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "products" ("id" TEXT, "name" TEXT, "description" TEXT, "price" INTEGER, "url" TEXT, "stock" TEXT, "one" TEXT, "two" TEXT, "three" TEXT, "ctg" TEXT, "video" TEXT);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "users" ("id" TEXT, "pw" TEXT,"ip" TEXT, "money" INTEGER, "buylog" TEXT, "isadmin" INTEGER, "black" TEXT, "name" TEXT, "tag" TEXT, "fail" INTEGER, "sms" INTEGER, "ranks" TEXT, "bought" INTEGER, "download" TEXT, "chargelog" TEXT);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "bankwait" ("id" TEXT, "name" TEXT, "amount" INTEGER, "day" TEXT);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "links" ("id" TEXT, "name" TEXT, "link" TEXT);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "category" ("id" TEXT, "name" TEXT);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "redeem" ("code" TEXT, "money" INTEGER, "used" INTEGER);""")
                                    con.commit()
                                    cur.execute("""CREATE TABLE "popup" ("popup_text" TEXT, "popup_img" TEXT);""")
                                    con.commit()
                                    cur.execute("""INSERT INTO info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (request.form["name"], "", "", "", "[]", "[]", "", make_expiretime(license_result[1]), "", "공지가 없습니다.", 0, "", "", 0 if license_result[5] == 0 else 1, "", "https://media.tenor.com/FIlAXMHf8vsAAAAd/naruto-background.gif", "", "https://cdn.discordapp.com/attachments/961867193665069066/1008758480775151726/NONE.png", "사용함", "", "", "", "", 0, 0, 0, 0, 0, 0, "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "SA NC Service", "https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", 0, 0, 0, 0, 0))
                                    con.commit()
                                    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (request.form["adminid"], hash(request.form["adminpw"]), getip(), 0, "[]", 1, "", "", "", "0", 0, "비구매자", 0, "[]", "[]"))
                                    con.commit()
                                con.close()

                                api_key = "클플 api"
                                email = "클플 메일"
                                zone_id = "클플 지역 아이디"

                                headers = {"X-Auth-Email" : email, "X-Auth-Key" : api_key}
                                json_data = {"type" : "A", "name" : request.form["url"], "content" : "커넥션 아이피", "ttl" : 1, "proxied" : True}
                                try:
                                    res_data = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=headers, json=json_data).json()
                                except:
                                    pass
                                return "ok"
                            else:
                                return "reCAPTCHA 오류가 발생했습니다. 새로고침 후 재시도해주세요."
                        else:
                            return "이미 존재하는 URL입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                return '"로봇이 아닙니다" 를 눌러주세요.'


@app.route("/", subdomain='<name>', methods=["GET"])
def index(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    return redirect("../notice")
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/login", subdomain='<name>', methods=["GET", "POST"])
def login(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        return redirect("../notice")
                    else:
                        info = get_info(name)
                        if (str(info[6]) != ""):
                            return render_template("403.html", reason=info[6])
                        else:
                            return render_template("logins.html", name=info[0], info=info, background=info[15])
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        return redirect("shop")
                    else:
                        if ("id" in request.form and "pw" in request.form):
                            user_info = search_user(name, request.form["id"])
                            if (user_info != None):
                                if (user_info[1] == hash(request.form["pw"])):
                                    if (user_info[6] == ""):
                                        server_info = get_info(name)
                                        session[name] = request.form["id"]
                                        if (server_info[19] != None):
                                            try:
                                                if not (user_info[5] == 1):
                                                    con = sqlite3.connect(db(name))
                                                    cur = con.cursor()
                                                    cur.execute("UPDATE info SET day = ?, week = ?, month = ?", (server_info[47] + 1, server_info[48] + 1, server_info[49] + 1))
                                                    con.commit()
                                                    con.close()
                                                else:
                                                    webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                                    embed = DiscordEmbed(title='🔔 로그인 알림', description=f'서버이름: {server_info[0]}\n────────────────\n아이디: {request.form["id"]}\n로그인 날짜: {nowstr()}\n────────────────', color=0x010101)
                                                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                                    embed.set_footer(text="SA NC SERVICE")
                                                    webhook.add_embed(embed)
                                                    webhook.execute()
                                            except:
                                                print("Webhook Error")
                                        return '<script>window.location.href = "notice"</script>'
                                    else:
                                        reason = user_info[6]
                                        return f'<script>alert(`관리자에 의해 차단된 계정입니다.\n차단 사유 : {reason}`); window.location.href = "login";</script>'
                                else:
                                    return '<script>alert("비밀번호가 틀렸습니다."); window.location.href = "login"</script>'
                            else:
                                return '<script>alert("아이디가 틀렸습니다."); window.location.href = "login"</script>'
                        else:
                            return '<script>alert("잘못된 접근입니다."); window.location.href = "login"</script>'
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/register", subdomain='<name>', methods=["GET", "POST"])
def register(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        return redirect("shop")
                    else:
                        info = get_info(name)
                        if (str(info[6]) != ""):
                            return render_template("403.html", reason=info[6])
                        elif (is_expired(info[7])):
                            return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                        else:
                            return render_template("register.html", name=info[0], info=info, background=info[15])
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        return redirect("shop")
                    else:
                        if ("id" in request.form and "pw" in request.form):
                            user_info = search_user(name, request.form["id"])
                            if (user_info == None):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("SELECT * FROM users WHERE ip == ?;", (getip(),))
                                iplist = cur.fetchone()
                                con.close()
                                if (iplist == None):
                                    if ((len(request.form["id"]) >= 6 and len(request.form["id"]) <= 24) and (len(request.form["pw"]) >= 6 and len(request.form["pw"]) <= 24)):
                                        con = sqlite3.connect(db(name))
                                        cur = con.cursor()
                                        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (request.form["id"], hash(request.form["pw"]), getip(), 0, "[]", 0, "", "", request.form["tag"], "0", 0, "비구매자", 0, "[]", "[]"))
                                        con .commit()
                                        con.close()
                                        session.pop(name, None)
                                        session[name] = request.form["id"]
                                        server_info = get_info(name)
                                        if (server_info[19] != None):
                                            try:
                                                con = sqlite3.connect(db(name))
                                                cur = con.cursor()
                                                cur.execute("UPDATE info SET day = ?, week = ?, month = ?", (server_info[47] + 1, server_info[48] + 1, server_info[49] + 1))
                                                con.commit()
                                                con.close()
                                                webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                                embed = DiscordEmbed(title=f'🔔 회원가입 알림', description=f'────────────────\n서버이름: {server_info[0]}\n가입한 아이디: {request.form["id"]}\n디스코드 닉네임: {request.form["tag"]}\n아이피: {getip()}\n회원가입 날짜: {nowstr()}\n────────────────', color=0x010101)
                                                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                                embed.set_footer(text="SA NC SERVICE")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                            except:
                                                print("Webhook Error")
                                        return '<script>alert("회원가입에 성공했습니다!"); window.location.href = "login"</script>'
                                    else:
                                        return '<script>alert("아이디 및 암호는 6 ~ 24자입니다."); window.location.href = "register?agreed=true"</script>'
                                else:
                                    return '<script>alert("이미 해당 IP로 가입된 계정이 있습니다."); window.location.href = "register?agreed=true"</script>'
                            else:
                                return '<script>alert("이미 존재하는 아이디입니다."); window.location.href = "register?agreed=true"</script>'
                        else:
                            return '<script>alert("잘못된 접근입니다."); window.location.href = "register?agreed=true"</script>'
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/shop", subdomain='<name>', methods=["GET"])
def shop(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (str(info[6]) != ""):
                        return render_template("403.html", reason=info[6])
                    elif (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    else:
                        
                        server_info = get_info(name)
                        user_info = search_user(name, session[name])
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM category")
                        ctg = cur.fetchall()
                        con.close()
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM links;")
                        links = cur.fetchall()
                        con.close()
                        money = "{:,}".format(int(user_info[3]))
                        buylog = ast.literal_eval(server_info[4])
                        if (request.args.get("id", "")):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products WHERE ctg == ?;", (request.args.get("id", ""),))
                            products = cur.fetchall()
                            con.close()
                        else:
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products")
                            products = cur.fetchall()
                            con.close()

                        prods = []
                        for i in products:
                            prods.append([
                                i[0],
                                i[1],
                                i[2],
                                i[3],
                                i[4],
                                i[5],
                             ast.literal_eval(i[6]),
                            ast.literal_eval(i[7]),
                            ast.literal_eval(i[8])])
                        return render_template("index.html", buylog=buylog, money=money, sinfo=server_info, name=server_info[0], ctgs=ctg, products=prods, links=links, user_info=user_info, music=server_info[8], shopinfo=server_info, linking=server_info[14], url=name, file=info[16], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/history/charge", subdomain='<name>', methods=["GET"])
def chargelog(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    """if (request.args.get("type", "") == "all"):
                        info = search_user(name, session[name])
                        server_info = get_info(name)
                        buylog_list = ast.literal_eval(server_info[4])
                        return render_template("log.html", infos=info[4], user_info=info, name=server_info[0], logs=reversed(sorted(buylog_list)), music=server_info[8], shopinfo=server_info, linking=server_info[14], type=0, url=name, file=server_info[16], channelio=server_info[21])
                    else:"""
                    info = search_user(name, session[name])
                    server_info = get_info(name)
                    charge_list = ast.literal_eval(info[14])
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM links;")
                    links = cur.fetchall()
                    con.close()
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category")
                    ctg = cur.fetchall()
                    con.close()
                    money = "{:,}".format(int(info[3]))
                    buylog = ast.literal_eval(server_info[4])
                    return render_template("chargelog.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], logs=reversed(sorted(charge_list)), music=server_info[8], shopinfo=server_info, linking=server_info[14], type=1, url=name, file=server_info[16], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/history", subdomain='<name>', methods=["GET"])
def log(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    """if (request.args.get("type", "") == "all"):
                        info = search_user(name, session[name])
                        server_info = get_info(name)
                        buylog_list = ast.literal_eval(server_info[4])
                        return render_template("log.html", infos=info[4], user_info=info, name=server_info[0], logs=reversed(sorted(buylog_list)), music=server_info[8], shopinfo=server_info, linking=server_info[14], type=0, url=name, file=server_info[16], channelio=server_info[21])
                    else:"""
                    info = search_user(name, session[name])
                    server_info = get_info(name)
                    all_list = ast.literal_eval(server_info[4])
                    down_list = ast.literal_eval(info[13])
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM links;")
                    links = cur.fetchall()
                    con.close()
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category")
                    ctg = cur.fetchall()
                    con.close()
                    money = "{:,}".format(int(info[3]))
                    buylog = ast.literal_eval(server_info[4])
                    return render_template("log.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], download=reversed(sorted(down_list)), logs=reversed(sorted(buylog)), alllogs=reversed(sorted(all_list)), music=server_info[8], shopinfo=server_info, linking=server_info[14], type=1, url=name, file=server_info[16], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/notice", subdomain='<name>', methods=["GET"])
def announcement(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    info = search_user(name, session[name])
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM links;")
                    links = cur.fetchall()
                    con.close()
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category")
                    ctg = cur.fetchall()
                    con.close()
                    money = "{:,}".format(int(info[3]))

                    server_info = get_info(name)

                    buylog = ast.literal_eval(server_info[4])

                    return render_template("html.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/redeem", subdomain='<name>', methods=["GET", "POST"])
def redeem(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "POST"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        if ("code" in request.get_json()):
                            info = search_user(name, session[name])
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM redeem WHERE code == ?", (request.get_json()["code"],))
                            redeem = cur.fetchone()
                            con.close()
                            if (redeem != None):
                                if (redeem[2] == 0):
                                    user_info = search_user(name, session[name])
                                    now_money = int(user_info[3])
                                    new_money = now_money + int(redeem[1])
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?", (new_money, session[name]))
                                    con.commit()
                                    cur.execute("UPDATE redeem SET used = ? WHERE code == ?", (1, request.get_json()["code"]))
                                    con.commit()
                                    con.close()
                                    return "ok|" + str(redeem[1])
                                else:
                                    return "이미 사용된 쿠폰입니다."
                            else:
                                return "존재하지 않는 쿠폰입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return redirect("../login")
                else:
                    abort(404)
            else:
                abort(404)
        else:

            server_info = get_info(name)
            info = search_user(name, session[name])
            con = sqlite3.connect(db(name))
            cur = con.cursor()
            cur.execute("SELECT * FROM links;")
            links = cur.fetchall()
            cur.execute("SELECT * FROM category")
            ctg = cur.fetchall()
            con.close()
            money = "{:,}".format(int(info[3]))
            if (is_expired(server_info[7])):
                return render_template("403.html", reason="라이센스 연장이 필요합니다.")
            return render_template("redeem.html", money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
            

@app.route("/introduce", subdomain='<name>', methods=["GET"])
def introduce(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    info = search_user(name, session[name])
                    product = search_prod(name, request.args.get("id", ""))
                    server_info = get_info(name)
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM links;")
                    links = cur.fetchall()
                    con.close()
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category")
                    ctg = cur.fetchall()
                    con.close()
                    money = "{:,}".format(int(info[3]))
                    buylog = ast.literal_eval(server_info[4])
                    return render_template("introduce.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, prod_name=product[1], prod_introduce=product[2], links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/video", subdomain='<name>', methods=["GET"])
def video(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    info = get_info(name)
                    if (is_expired(info[7])):
                        return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                    info = search_user(name, session[name])
                    product = search_prod(name, request.args.get("id", ""))
                    server_info = get_info(name)
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM links;")
                    links = cur.fetchall()
                    con.close()
                    con = sqlite3.connect(db(name))
                    cur = con.cursor()
                    cur.execute("SELECT * FROM category")
                    ctg = cur.fetchall()
                    con.close()
                    money = "{:,}".format(int(info[3]))
                    buylog = ast.literal_eval(server_info[4])
                    return render_template("video.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, prod_name=product[1], prod_video=product[10], links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                else:
                    return redirect("../login")
            else:
                abort(404)
        else:
            abort(404)


@app.route("/buy", subdomain='<name>', methods=["GET", "POST"])
def buy(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    if ("id" in request.get_json() and "amount" in request.get_json() and 'type' in request.get_json()):
                        prod_info = get_prod(name, request.get_json()["id"])
                        if (prod_info != None):
                            reqj = request.get_json()
                            buy_type = None
                            if reqj['type'] == 1:
                                buy_type = 6
                            elif reqj['type'] == 2:
                                buy_type = 7
                            elif reqj['type'] == 3:
                                buy_type = 8

                            if buy_type is None:
                                return TypeError

                        server_info = get_info(name)
                        user_info = search_user(name, session[name])
                        prodo = ast.literal_eval(prod_info[buy_type])
                        if (len(prodo[2].split("\n")) >= int(request.get_json()["amount"])):
                            if user_info[11] == "비구매자":
                                rank = server_info[24]
                            if user_info[11] == "구매자":
                                rank = server_info[25]
                            if user_info[11] == "VIP":
                                rank = server_info[26]
                            if user_info[11] == "VVIP":
                                rank = server_info[27]
                            if user_info[11] == "리셀러":
                                rank = server_info[28]

                            
                            prodo = ast.literal_eval(prod_info[buy_type])
                            if (prodo[2] != "" and str(request.get_json()["amount"]).isdigit() and request.get_json()["amount"] > 0 and len(prodo[2].split("\n")) >= request.get_json()["amount"]):
                                user_info = search_user(name, session[name])
                                total_price = int(list(prodo)[1] * int(request.get_json()["amount"]) * rank/100)
                                buy_money = int(str(list(prodo)[1] * int(request.get_json()["amount"]) - total_price).split(".")[0])
                                if (int(user_info[3]) >= int(list(prodo)[1] * int(request.get_json()["amount"]) - total_price)):
                                    con = sqlite3.connect(db(name))
                                    with con:
                                        

                                        now_stock = prodo[2].split("\n")
                                        bought_stock = []
                                        for n in range(request.get_json()["amount"]):
                                            choiced_stock = random.choice(now_stock)
                                            bought_stock.append(choiced_stock)
                                            now_stock.remove(choiced_stock)
                                    
                                        bought_stock = "\n".join(bought_stock)
                                        now_money = int(user_info[3]) - buy_money
                                        now_bought = int(user_info[12]) + buy_money
                                        now_buylog = ast.literal_eval(user_info[4])
                                        name1 = (prod_info[1])
                                        typing = f"{session[name]}님, {prodo[0]} 구매 감사합니다!"
                                        now_buylog.append([nowstr(), prodo[0], buy_money, bought_stock, request.get_json()["amount"]])
                                        cur = con.cursor()
                                        cur.execute("UPDATE users SET money = ?, buylog = ?, download = ? WHERE id == ?", (now_money, str(now_buylog), str(now_buylog), session[name]))
                                        con.commit()
                                        cur.execute("UPDATE users SET bought = ? WHERE id == ?", (now_bought, session[name]))
                                        con.commit()
                                        if user_info[11] == "비구매자":
                                            cur.execute("UPDATE users SET ranks = ? WHERE id == ?", ("구매자", session[name]))
                                            con.commit()
                                        if buy_type == 6:
                                            cur.execute("UPDATE products SET one = ? WHERE id == ?", (str([prodo[0],int(prodo[1]), "\n".join(now_stock)]), request.get_json()["id"]))
                                            con.commit()
                                        elif buy_type == 7:
                                            cur.execute("UPDATE products SET two = ? WHERE id == ?", (str([prodo[0],int(prodo[1]), "\n".join(now_stock)]), request.get_json()["id"]))
                                            con.commit()
                                        elif buy_type == 8:
                                            cur.execute("UPDATE products SET three = ? WHERE id == ?", (str([prodo[0],int(prodo[1]), "\n".join(now_stock)]), request.get_json()["id"]))
                                            con.commit()
                                        server_info = get_info(name)
                                        buylog = ast.literal_eval(server_info[4])
                                        buylog.append([nowstr(), (session[name])[:4], prodo[0], name1 , bought_stock])
                                        cur.execute("UPDATE info SET buylog = ?", (str(buylog),))
                                        con.commit()
                                    con.close()
                                    try:
                                        if now_bought >= server_info[29]:
                                            con = sqlite3.connect(db(name))
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET ranks = ? WHERE id == ?;", ("VIP", session[name]))
                                            con.commit()
                                            con.close()
                                        if now_bought >= server_info[30]:
                                            con = sqlite3.connect(db(name))
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET ranks = ? WHERE id == ?;", ("VVIP", session[name]))
                                            con.commit()
                                            con.close()
                                        if now_bought >= server_info[31]:
                                            con = sqlite3.connect(db(name))
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET ranks = ? WHERE id == ?;", ("리셀러", session[name]))
                                            con.commit()
                                        con.close()
                                    except:
                                        pass
                                    try:
                                        user_name = session[name][:-4] + "****"
                                        server_info = get_info(name)
                                        prod_amount = str(request.get_json()["amount"])
                                        if (name == "dench"):
                                            webhook = DiscordWebhook(username=server_info[45], avatar_url=server_info[46], url=server_info[1])
                                            embed = DiscordEmbed(title=f'`💵 {server_info[0]} 구매로그`', description="`" + user_name + "님, " + prodo[0] + " " + prod_amount + "개 구매 감사합니다! 💝`", color=0x010101)
                                            embed.set_thumbnail(url=prod_info[4])
                                            embed.set_footer(text=server_info[0], icon_url=server_info[46])
                                            embed.set_timestamp()
                                            webhook.add_embed(embed)
                                            webhook.execute()
                                        else:
                                            webhook = DiscordWebhook(username=server_info[45], avatar_url=server_info[46], url=server_info[1])
                                            embed = DiscordEmbed(title=f'`💵 구매로그`', description="`" + user_name + "님, " + prodo[0] + " " + prod_amount + "개 구매 감사합니다! 💝`", color=0x010101)
                                            embed.set_thumbnail(url=prod_info[4])
                                            embed.set_footer(text=server_info[0], icon_url=server_info[46])
                                            embed.set_timestamp()
                                            webhook.add_embed(embed)
                                            webhook.execute()

                                        if (server_info[19] != None):
                                            try:
                                                webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                                embed = DiscordEmbed(title=f'🔔 제품 구매 알림', description=f'서버이름: {server_info[0]}\n────────────────\n아이디: {session[name]}\n아이피: {getip()}\n구매한 제품: {prodo[0]}\n구매한 재고: {bought_stock}\n구매날짜: {nowstr()}\n────────────────', color=0x010101)
                                                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                                embed.set_footer(text="SA NC SERVICE")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                            except:
                                                print("Webhook Error")
                                    except:
                                        pass
                                    
                                    return "ok"
                                else:
                                    return "잔액이 부족합니다."
                            else:
                                return "재고가 부족합니다."
                        else:
                            return "알 수 없는 오류입니다."
                    else:
                        return "로그인이 해제되었습니다. 다시 로그인해주세요."
                else:
                    return "로그인이 해제되었습니다. 다시 로그인해주세요."
            else:
                abort(404)
        else:
            abort(404)

@app.route("/culture/charge", subdomain='<name>', methods=["GET" ,"POST"])
def moonsang(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "POST"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        if ("code1" in request.get_json() and "code2" in request.get_json() and "code3" in request.get_json() and "code4" in request.get_json()):
                            server_info = get_info(name)
                            culture_id = server_info[2]
                            culture_pw = server_info[3]
                            keeplogincookie = server_info[50]
                            if (culture_id != "" and culture_pw != ""):
                                try:
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM users WHERE id == ?;", (session[name],))
                                    chargereq_info = cur.fetchone()
                                    if not server_info[23] == 0:
                                        if chargereq_info[10] == 0:
                                            return f'<script>alert(`위 서버는 SMS 인증이 필수입니다.`); window.location.href = "smsverify";</script>'
                                    if chargereq_info[6] != "":
                                        return f"자판기에서 차단당한 유저는 충전이 불가능합니다.<br>사유: {chargereq_info[6]}"
                                    if chargereq_info[9] == 3:
                                        return "관리자에게 문의해주세요. ( 누적 충전 실패 횟수 )"
                                    pin1 = request.get_json()["code1"]
                                    pin2 = request.get_json()["code2"]
                                    pin3 = request.get_json()["code3"]
                                    pin4 = request.get_json()["code4"]
                                    code = f"{pin1}-{pin2}-{pin3}-{pin4}"
                                    jsondata = {"token" : "문상자충", "keepLoginInfo" : keeplogincookie, "pin" : code}
                                    res = requests.post("문상자충", json=jsondata)
                                    if ( ):
                                        raise TypeError
                                    else:
                                        res = res.json()
                                        # try:
                                        #     res = res.json()
                                        #     print(f"문상충전 알림 : {str(res)}")
                                        #     webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url="https://discord.com/api/webhooks/842029711981936681/K9lB4iAGbEruwgfPi_b0QUPm2uVcKrXWC2q12hvu7MNNqTsIvgX1W_TgcWwwRQkBdXz9")
                                        #     embed = DiscordEmbed(title=f"문상충전 알림 : {str(res)}\n\n서버이름 : {server_info[0]}\n\n아이디 : {session[name]}", color=0x010101)
                                        #     webhook.add_embed(embed)
                                        #     webhook.execute()
                                        # except:
                                        #     print("Webhook Error")

                                        if (server_info[19] != None):
                                            try:
                                                webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                                embed = DiscordEmbed(title=f'🔔 문상 충전 알림', description=f'서버이름: {server_info[0]}\n────────────────\n아이디: {session[name]}\n신청날짜: {nowstr()}\n충전결과: {str(res)}\n────────────────', color=0x010101)
                                                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                                embed.set_footer(text="SA NC SERVICE")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                            except:
                                                print ("Webhook Error")
                                except:
                                    return "서버 에러가 발생했습니다."

                                pin1 = request.get_json()["code1"]
                                pin2 = request.get_json()["code2"]
                                pin3 = request.get_json()["code3"]
                                pin4 = request.get_json()["code4"]
                                code = f"{pin1}-{pin2}-{pin3}-{pin4}"

                                if (res["result"] == True):
                                    user_info = search_user(name, session[name])
                                    if user_info[11] == "비구매자":
                                        fee = server_info[35]
                                        event = server_info[40]
                                    if user_info[11] == "구매자":
                                        fee = server_info[36]
                                        event = server_info[41]
                                    if user_info[11] == "VIP":
                                        fee = server_info[37]
                                        event = server_info[42]
                                    if user_info[11] == "VVIP":
                                        fee = server_info[38]
                                        event = server_info[43]
                                    if user_info[11] == "리셀러":
                                        fee = server_info[39]
                                        event = server_info[44]
                                    culture_amount = int(res["amount"])
                                    now_amount = ((culture_amount / 100) * (100 - fee))
                                    new_amount = ((now_amount / 100) * (100 + event)) + int(user_info[3])
                                    see = ((now_amount / 100) * (100 + event))
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?", (new_amount, session[name]))
                                    con.commit()
                                    con.close()
                                    server_info = get_info(name)
                                    chargelog = ast.literal_eval(server_info[5])
                                    chargelog.append([nowstr(), session[name], code, "충전 완료", str(culture_amount)])
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE info SET chargelog = ?", (str(chargelog),))
                                    con.commit()
                                    cur.execute("UPDATE info SET mm = ?, totalm = ?", (server_info[33] + int(culture_amount), server_info[34] + int(culture_amount),))
                                    con.commit()
                                    user_info = search_user(name, session[name])
                                    chargelogs = ast.literal_eval(user_info[14])
                                    chargelogs.append([nowstr(), code, str(culture_amount), "충전 완료"])
                                    cur.execute("UPDATE users SET chargelog = ? WHERE id == ?;", (str(chargelogs), session[name]))     
                                    con.commit()  
                                    con.close()
                                    return "ok|" + str(see)
                                else:
                                    server_info = get_info(name)
                                    chargelog = ast.literal_eval(server_info[5])
                                    chargelog.append([nowstr(), session[name], code, res["reason"], "0"])
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE info SET chargelog = ?", (str(chargelog),))
                                    con.commit()
                                    con.close()
                                    user_info = search_user(name, session[name])
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET fail = ?", (user_info[9] + 1,))
                                    con.commit()
                                    con.close()
                                    return str(res["reason"])
                            else:
                                return "이 상점에서는 문화상품권으로 충전할 수 없습니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "로그인이 해제되었습니다. 다시 로그인해주세요."
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        
                        info = get_info(name)
                        if (is_expired(info[7])):
                            return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                        info = search_user(name, session[name])
                        server_info = get_info(name)
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM links;")
                        links = cur.fetchall()
                        con.close()
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM category")
                        ctg = cur.fetchall()
                        con.close()
                        money = "{:,}".format(int(info[3]))
                        buylog = ast.literal_eval(server_info[4])
                        return render_template("moonsang.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                    else:
                        return redirect("../login")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/bank/charge", subdomain='<name>', methods=["GET", "POST"])
def bank(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "POST"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        if ("name" in request.get_json() and "amount" in request.get_json() and request.get_json()["amount"].isdigit()):
                            bankname = request.get_json()["name"]
                            amount = request.get_json()["amount"]
                            server_info = get_info(name)

                            

                            if (server_info[22].isdigit()):
                                if (server_info[22] != "" and int(amount) < int(server_info[22])):
                                    return f"최소 충전금액은 {server_info[22]}원입니다."
                            bank_addr = server_info[11]
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE id == ?;", (session[name],))
                            chargereq_info = cur.fetchone()
                            if not server_info[23] == 0:
                                if chargereq_info[10] == 0:
                                    return f'<script>alert(`위 서버는 SMS 인증이 필수입니다.`); window.location.href = "smsverify";</script>'
                            if chargereq_info[6] != "":
                                return f"자판기에서 차단당한 유저는 충전이 불가능합니다.<br>사유: {chargereq_info[6]}"
                            if (server_info[13] == 0):
                                abort(401)
                            if (bank_addr != ""):
                                con = sqlite3.connect(db(name))
                                with con:
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM bankwait WHERE id == ?;", (session[name],))
                                    chargereq_info = cur.fetchone()
                                    if (chargereq_info != None):
                                        return "이미 진행 중인 충전 신청이 있습니다.<br>입금 계좌 : " + server_info[11] + "<br>신청 금액: " + str(chargereq_info[2]) + "원, 입금자명: " + chargereq_info[1]
                                    else:
                                        cur.execute("SELECT * FROM users WHERE id == ?;", (session[name],))
                                        user_info = cur.fetchone()
                                        if (user_info[7] != ""):
                                            if (user_info[7] != bankname):
                                                return "잘못된 접근입니다."
                                            else:
                                                pass
                                        else:
                                            cur.execute("UPDATE users SET name = ? WHERE id == ?;", (bankname, session[name]))
                                            con.commit()
                                        cur.execute("INSERT INTO bankwait VALUES(?, ?, ?, ?);", (session[name], bankname, amount, nowstr()))
                                        con.commit()
                                con.close()
                                if (server_info[19] != None):
                                    try:
                                        server_info = get_info(name)
                                        webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                        embed = DiscordEmbed(title='🔔 계좌 충전신청 알림', description=f'서버이름: {server_info[0]}\n────────────────\n아이디: {session[name]}\n입금계좌: {server_info[11]}\n입금자명: {bankname}\n입금금액: {amount}\n신청날짜: {nowstr()}\n────────────────', color=0x010101)
                                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                        embed.set_footer(text="SA NC SERVICE")
                                        webhook.add_embed(embed)
                                        webhook.execute()
                                    except:
                                        print("Webhook Error")
                                    names = session[name]
                                    def waiting():
                                        server_info = get_info(name)
                                        jsondata = {
                                            "api_key": "계좌토", "bankpin": str(server_info[12]), "shop": str(server_info[0]), "userinfo": str(bankname), "userid": str(names), "token": "token", "type": True, "amount": int(amount)
                                        }

                                        ms_result = requests.post(
                                            "http://bankapi.lol:8080/bank", json=jsondata)
                                        ms_result = ms_result.json()

                                        if ms_result["result"] == False:
                                            try:
                                                reason = ms_result["reason"]
                                                webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/914802606348578858/920600613014863912/-1.png", url=server_info[19])
                                                embed = DiscordEmbed(title='🔔 계좌 충전실패 알림', description=f'서버이름 : {server_info[0]}\n────────────────\n입금계좌: {server_info[11]}\n입금자명: {bankname}\n아이디: {names}\n입금금액: {amount}\n실패사유: {reason}\n실패날짜: {nowstr()}\n────────────────', color=0x010101)
                                                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914802606348578858/920600613014863912/-1.png")
                                                embed.set_footer(text="SA NC SERVICE")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                            except:
                                                print("Webhook Error")                                     


                                            con = sqlite3.connect(db(name))
                                            cur = con.cursor()
                                            cur.execute("DELETE FROM bankwait WHERE id == ?;", (names,))
                                            con.commit()
                                            con.close()

                                        if ms_result["result"] == True:
                                            if ms_result["id"] == names:
                                                count = ms_result["count"]
                                                server_info = get_info(name)
                                                user_info = search_user(name, names)
                                                con = sqlite3.connect(db(name))
                                                cur = con.cursor()
                                                cur.execute("UPDATE users SET money = money + ? WHERE id == ?", (count, names))
                                                con.commit()                    
                                                cur.execute("UPDATE info SET bankm = ?, totalm = ?", (server_info[32] + int(count), server_info[34] + int(count),))
                                                con.commit()
                                                chargelog = ast.literal_eval(user_info[14])
                                                chargelog.append([nowstr(), str(bankname), str(count), "충전 완료"])
                                                cur.execute("UPDATE users SET chargelog = ? WHERE id == ?;", (str(chargelog), names))     
                                                con.commit()    
                                                con.close()
                                                try:
                                                    webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/914802606348578858/920600613014863912/-1.png", url=server_info[19])
                                                    embed = DiscordEmbed(title='🔔 계좌 충전성공 알림', description=f'서버이름 : {server_info[0]}\n────────────────\n입금계좌: {server_info[11]}\n입금자명: {bankname}\n아이디: {names}\n입금금액: {amount}\n충전금액: {count}\n충전날짜: {nowstr()}\n────────────────', color=0x010101)
                                                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/914802606348578858/920600613014863912/-1.png")
                                                    embed.set_footer(text="SA NC SERVICE")
                                                    webhook.add_embed(embed)
                                                    webhook.execute()
                                                except:
                                                    print("Webhook Error")    
                                                
                                                con = sqlite3.connect(db(name))
                                                cur = con.cursor()
                                                cur.execute("DELETE FROM bankwait WHERE id == ?;", (names,))
                                                con.commit()
                                                con.close()

                                    try:
                                        t1 = threading.Thread(
                                            target=waiting, args=())
                                        t1.start()
                                    except Exception as e:
                                        print(f"Thrading Error\n{e}")


                                return "ok"
                            else:
                                return "이 상점에서는 계좌이체로 충전할 수 없습니다."
                        else:
                            return "충전 금액은 숫자로만 입력해주세요."
                    else:
                        return "로그인이 해제되었습니다. 다시 로그인해주세요."
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        info = get_info(name)
                        if (info[13] == 0):
                            abort(404)
                        if (is_expired(info[7])):
                            return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                        info = search_user(name, session[name])
                        server_info = get_info(name)
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM links;")
                        links = cur.fetchall()
                        con.close()
                        con = sqlite3.connect(db(name))
                        cur = con.cursor()
                        cur.execute("SELECT * FROM category")
                        ctg = cur.fetchall()
                        con.close()
                        money = "{:,}".format(int(info[3]))
                        buylog = ast.literal_eval(server_info[4])
                        return render_template("bank.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                    else:
                        return redirect("../login")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/mypage", subdomain='<name>', methods=["GET", "POST"])
def mypages(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        info = get_info(name)
                        if (is_expired(info[7])):
                            return render_template("403.html", reason="라이센스 연장이 필요합니다.")
                        else:
                            server_info = get_info(name)
                            user_info = search_user(name, session[name])
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM links;")
                            links = cur.fetchall()
                            con.close()
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category")
                            ctg = cur.fetchall()
                            con.close()
                            money = "{:,}".format(int(user_info[3]))
                            buylog = ast.literal_eval(server_info[4])
                            return render_template("password.html", buylog=buylog, money=money, sinfo=server_info, infos=info[4], ctgs=ctg, links=links, user_info=user_info, name=server_info[0], music=server_info[8], announcement=server_info[9], shopinfo=server_info, linking=server_info[14], url=name, file=server_info[16], imgannouncement=server_info[17], channelio=server_info[21])
                    else:
                        return redirect("../login")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        if ("nowpw" in request.get_json() and "pw" in request.get_json() and "pwcheck" in request.get_json()):
                            user_info = search_user(name, session[name])
                            if (user_info[1] == hash(request.get_json()["nowpw"])):
                                if (request.get_json()["pw"] == request.get_json()["pwcheck"]):
                                    if (len(request.get_json()["pw"]) >= 6 and len(request.get_json()["pw"]) <= 24):
                                        con = sqlite3.connect(db(name))
                                        cur = con.cursor()
                                        cur.execute("UPDATE users SET pw = ? WHERE id == ?", (hash(request.get_json()["pw"]), session[name]))
                                        con.commit()
                                        con.close()
                    
                                        server_info = get_info(name)
                                        if (server_info[19] != None):
                                            try:
                                                webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[19])
                                                embed = DiscordEmbed(title='🔔 비밀번호 변경 알림', description=f'서버이름: {server_info[0]}\n────────────────\n변경자: {session[name]}\n변경날짜: {nowstr()}\n────────────────', color=0x010101)
                                                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png")
                                                embed.set_footer(text="SA NC SERVICE")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                            except:
                                                    print("Webhook Error")
                                            return "ok"
                                    else:
                                        return "암호는 6 ~ 24자입니다."
                                else:
                                    return "비밀번호 확인이 일치하지 않습니다."
                            else:
                                return "현재 비밀번호가 틀립니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return redirect("../login")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/", subdomain='<name>', methods=["GET"])
def admin(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        return redirect("setting")
                    else:
                        return redirect("../shop")
                else:
                    return redirect("../shop")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/setting", subdomain='<name>',methods=["GET", "POST"])
def setting(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            if (server_info[50] == ""):
                                jsondata = {"token": "47c2d5ea-8d78-4126-b0d6-e5a39d006c6a", "keepLoginInfo": server_info[50] }
                                res = requests.post("http://123.141.95.98/balance", json=jsondata)
                                res = res.json()
                                amount = int(res["amount"])
                                cur.execute("UPDATE info SET cash == ? ", (amount, ))
                                con.commit()
                            else:
                                cur.execute("SELECT * FROM users")
                                users = cur.fetchall()
                                alluser = len(users)
                                cur.execute("SELECT * FROM users WHERE ranks == ?;", ("비구매자",))
                                nusers = cur.fetchall()
                                nbuyuser = len(nusers)
                                cur.execute("SELECT * FROM users WHERE ranks == ?;", ("구매자",))
                                busers = cur.fetchall()
                                buyuser = len(busers)
                                con.close()

                            return render_template("admin_general.html", info=server_info, server_info=server_info, alluser=alluser, nbuyuser=nbuyuser, buyuser=buyuser)
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            
                            if ("name" in request.form and "cultureid" in request.form and "culturepw" in request.form and "keeplogincookie" in request.form and "buylogwebhk" in request.form and "music" in request.form and "announcement" in request.form and ("bankaddr" in request.form) if server_info[13] == 1 else True and ("bankpw" in request.form) if server_info[13] == 1 else True and "linking" in request.form and "background" in request.form and "file" in request.form and "imgannouncement" in request.form and "buylogwebhkt" in request.form and "adminlogwebhk" in request.form and "addstock" in request.form and "channeltok" in request.form and "bankmax" in request.form and "nobuyer" in request.form and "buyer" in request.form and "vipoff" in request.form and "vvipoff" in request.form and "reselloff" in request.form and "autovip" in request.form and "autovvip" in request.form and "autoresell" in request.form and "nbuyerfee" in request.form and "buyerfee" in request.form and "vipfee" in request.form and "vvipfee" in request.form and "rsellfee" in request.form and "nbuyevt" in request.form and "buyevt" in request.form and "vipevt" in request.form and "vvipevt" in request.form and "rsellevt" in request.form and "whname" in request.form and ("whimg" in request.form) if server_info[13] == 1 else True):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("UPDATE info SET name = ?, cultureid = ?, culturepw = ?, keeplogincookie = ?, webhk = ?, music = ?, announcement = ?, bankaddr = ?, bankpw = ?, linking = ?, background = ?, file = ?, imgannouncement = ?, buylogwebhkt = ?, adminlogwebhk = ?, addstock = ?, channeltok = ?, bankmax = ?, nobuyer = ?, buyer = ?, vipoff = ?, vvipoff = ?, reselloff = ?, autovip = ?, autovvip = ?, autoresell = ?, nbuyerfee = ?, buyerfee = ?, vipfee = ?, vvipfee = ?, rsellfee = ?, nbuyevt = ?, buyevt = ?, vipevt = ?, vvipevt = ?, rsellevt = ?, whname = ?, whimg = ?;",(request.form["name"], request.form["cultureid"], request.form["culturepw"], request.form["keeplogincookie"], request.form["buylogwebhk"], request.form["music"], request.form["announcement"], request.form["bankaddr"] if server_info[13] == 1 else "", request.form["bankpw"] if server_info[13] == 1 else "", request.form["linking"], request.form["background"], request.form["file"], request.form["imgannouncement"], request.form["buylogwebhkt"], request.form["adminlogwebhk"], request.form["addstock"], request.form["channeltok"], request.form["bankmax"], request.form["nobuyer"], request.form["buyer"], request.form["vipoff"], request.form["vvipoff"], request.form["reselloff"], request.form["autovip"], request.form["autovvip"], request.form["autoresell"], request.form["nbuyerfee"], request.form["buyerfee"], request.form["vipfee"], request.form["vvipfee"], request.form["rsellfee"], request.form["nbuyevt"], request.form["buyevt"], request.form["vipevt"], request.form["vvipevt"], request.form["rsellevt"], request.form["whname"], request.form["whimg"] if server_info[13] == 1 else ""))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                abort(404)

@app.route("/admin/manageuser", subdomain='<name>', methods=["GET"])
def manageuser(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users;")
                            result = cur.fetchall()
                            con.close()
                            server_info = get_info(name)
                            return render_template("admin_manageuser.html", users=result, server_info=server_info)
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/manageuser_detail", subdomain='<name>', methods=["GET", "POST"])
def manageuser_detail(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            search_user_ = request.args.get("id", "")
                            if (search_user_ != ""):
                                user_info = search_user(name, search_user_)
                                if (user_info != None):
                                    server_info = get_info(name)
                                    return render_template("admin_manageuser_detail.html", info=user_info, server_info=server_info)
                                else:
                                    return redirect("manageuser")
                            else:
                                return redirect("manageuser")
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            if ("password" in request.form and "money" in request.form and "id" in request.form and "tag" in request.form and "fail" in request.form and "black" in request.form and "name" in request.form and "ranks" in request.form and ("bought" in request.form) if server_info[13] == 1 else True):
                                user_info = search_user(name, request.form["id"])
                                if (user_info != None):
                                    if (request.form["money"].isdigit()):
                                        con = sqlite3.connect(db(name))
                                        cur = con.cursor()
                                        if (server_info[13] == 1):
                                            cur.execute("SELECT * FROM users WHERE name == ?;", (request.form["name"],))
                                            user_name_info = cur.fetchone()
                                        if ((request.form["name"] == "" or user_name_info == None or user_name_info[0] == request.form["id"]) if server_info[13] == 1 else True):
                                            if (request.form["password"] == ""):
                                                cur.execute("UPDATE users SET money = ?, black = ?, name = ?, tag = ?, fail = ?, ranks = ?, bought = ? WHERE id == ?",(request.form["money"], request.form["black"], request.form["name"] if server_info[13] == 1 else "", request.form["tag"], request.form["fail"], request.form["ranks"], request.form["bought"], request.form["id"]))    
                                            else:
                                                cur.execute("UPDATE users SET pw = ?, money = ?, black = ?, name = ?, tag = ?, fail = ?, ranks = ?, bought = ? WHERE id == ?",(hash(request.form["password"]), request.form["money"], request.form["black"], request.form["name"] if server_info[13] == 1 else "", request.form["tag"], request.form["fail"], request.form["ranks"], request.form["bought"], request.form["id"]))
                                            con.commit()
                                            con.close()
                                        else:
                                            con.close()
                                            return "이미 존재하는 입금자명입니다."
                                        return "ok"
                                    else:
                                        return "잔액은 숫자로만 적어주세요."
                                else:
                                    return "잘못된 접근입니다."
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/manageprod", subdomain='<name>', methods=["GET"])
def manageprod(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM products;")
                            result = cur.fetchall()
                            con.close()
                            server_info = get_info(name)
                            return render_template("admin_manageprod.html", server_info=server_info, products=result)
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)


@app.route("/admin/createlink", subdomain='<name>', methods=["GET", "POST"])
def createlink(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            return render_template("admin_createlink.html", server_info=server_info)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("name" in request.form and "link" in request.form):
                                new_linkid = randomstring.pick(10)
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("INSERT INTO links VALUES(?, ?, ?);",
                                            (new_linkid, request.form["name"], request.form["link"]))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/managelink", subdomain='<name>', methods=["GET"])
def managelink(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM links;")
                            result = cur.fetchall()
                            con.close()
                            server_info = get_info(name)
                            return render_template("admin_managelink.html", server_info=server_info, info=result)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/managelink_detail", subdomain='<name>', methods=["GET", "POST"])
def managelink_detail(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            search_user_ = request.args.get("id", "")
                            if (search_user_ != ""):
                                user_info = search_link(name, search_user_)
                                if (user_info != None):
                                    server_info = get_info(name)
                                    return render_template("admin_managelink_detail.html", info=user_info, server_info=server_info)
                                else:
                                    return redirect("managelink")
                            else:
                                return redirect("managelink")
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            if ("name" in request.form and ("link" in request.form) if server_info[13] == 1 else True):
                                link_info = search_link(name, request.form["id"])
                                if (link_info != None):
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE links SET name = ?, link = ? WHERE id == ?", (request.form["name"], request.form["link"], request.form["id"]))
                                    con.commit()
                                    con.close()
                                    return "ok"
                                    
                                else:
                                    return "잘못된 접근입니다."
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/delete_link", subdomain='<name>', methods=["POST"])
def delete_link(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        if ("id" in request.form):
                            prod_info = search_link(name, request.form["id"])
                            if (prod_info != None):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("DELETE FROM links WHERE id == ?",(request.form["id"],))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/createredeem", subdomain='<name>', methods=["GET", "POST"])
def createredeem(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            return render_template("admin_createredeem.html", server_info=server_info)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("money" in request.form):
                                new_linkid = randomstring.pick(10)
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("INSERT INTO redeem VALUES(?, ?, ?);",
                                            (new_linkid, request.form["money"], 0))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/manageredeem", subdomain='<name>', methods=["GET"])
def manageredeem(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM redeem;")
                            result = cur.fetchall()
                            con.close()
                            server_info = get_info(name)
                            return render_template("admin_manageredeem.html", server_info=server_info, info=result)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/delete_redeem", subdomain='<name>', methods=["POST"])
def delete_redeem(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        if ("id" in request.form):
                            prod_info = search_redeem(name, request.form["id"])
                            if (prod_info != None):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("DELETE FROM redeem WHERE code == ?",(request.form["id"],))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/createcategory", subdomain='<name>', methods=["GET", "POST"])
def createcategory(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            return render_template("admin_createctg.html", server_info=server_info)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("name" in request.form):
                                new_linkid = randomstring.pick(10)
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("INSERT INTO category VALUES(?, ?);",
                                            (new_linkid, request.form["name"]))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/managecategory", subdomain='<name>', methods=["GET"])
def managecategory(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            con = sqlite3.connect(db(name))
                            cur = con.cursor()
                            cur.execute("SELECT * FROM category;")
                            result = cur.fetchall()
                            con.close()
                            server_info = get_info(name)
                            return render_template("admin_managectg.html", server_info=server_info, info=result)
                        else:
                            return redirect("../notice")
                    else:
                        return redirect("../notice")
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/managecategory_detail", subdomain='<name>', methods=["GET", "POST"])
def managecategory_detail(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            search_user_ = request.args.get("id", "")
                            if (search_user_ != ""):
                                user_info = search_ctg(name, search_user_)
                                if (user_info != None):
                                    server_info = get_info(name)
                                    return render_template("admin_managectg_detail.html", info=user_info, server_info=server_info)
                                else:
                                    return redirect("managecategory")
                            else:
                                return redirect("managecategory")
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            if ("name" in request.form):
                                link_info = search_ctg(name, request.form["id"])
                                if (link_info != None):
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    cur.execute("UPDATE category SET name = ? WHERE id == ?", (request.form["name"], request.form["id"]))
                                    con.commit()
                                    con.close()
                                    return "ok"
                                else:
                                    return "잘못된 접근입니다."
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/delete_category", subdomain='<name>', methods=["POST"])
def delete_category(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        if ("id" in request.form):
                            prod_info = search_ctg(name, request.form["id"])
                            if (prod_info != None):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("DELETE FROM category WHERE id == ?",(request.form["id"],))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                abort(404)
        else:
            abort(404)


@app.route("/admin/createprod", subdomain='<name>', methods=["GET", "POST"])
def createprod(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            return render_template("admin_createprod.html", server_info=server_info)
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("name" in request.form):
                                new_prodid = randomstring.pick(10)
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                                            (new_prodid, request.form["name"], "", "0", "", "", '[\'제품1\', 0, \'\']', '[\'제품2\', 0, \'\']', '[\'제품3\', 0, \'\']', "", ""))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/admin/manageprod_detail", subdomain='<name>', methods=["GET", "POST"])
def manageprod_detail(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            search_user_ = request.args.get("id", "")
                            if (search_user_ != ""):
                                user_info = search_prod(name, search_user_)
                                if (user_info != None):
                                    server_info = get_info(name)
                                    one = ast.literal_eval(user_info[6])
                                    two = ast.literal_eval(user_info[7])
                                    three = ast.literal_eval(user_info[8])
                                    return render_template("admin_manageprod_detail.html", info=user_info, server_info=server_info, one=one, two=two, three=three)
                                else:
                                    return redirect("manageprod")
                            else:
                                return redirect("manageprod")
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("name" in request.form and "description" in request.form and "photo" in request.form and "ctg" in request.form and  "video" in request.form and "id" in request.form and 'onename' in request.form and 'twoname'in request.form and 'threename' in request.form and 'oneprice' in request.form and 'twoprice' in request.form and 'threeprice' in request.form and 'onestock' in request.form and 'twostock' in request.form and 'threestock' in request.form):
                                prod_info = search_prod(name, request.form["id"])
                                if (user_info != None):
                                    if (request.form["name"] != ""):
                                        if (request.form["oneprice"].isdigit() and int(request.form["oneprice"]) > 0 and int(request.form["oneprice"]) <= 10000000 and request.form["twoprice"].isdigit() and int(request.form["twoprice"]) > 0 and int(request.form["twoprice"]) <= 10000000 and request.form["threeprice"].isdigit() and int(request.form["threeprice"]) > 0 and int(request.form["threeprice"]) <= 10000000):
                                            if (prod_info[5] != ""):
                                                nowstock = len(prod_info[5].split("\n"))
                                            con = sqlite3.connect(db(name))
                                            cur = con.cursor()
                                            cur.execute("UPDATE products SET name = ?, description = ?, url = ?, ctg = ?, video = ?, one = ?, two = ?, three = ? WHERE id == ?", (request.form["name"], request.form["description"], request.form["photo"], request.form["ctg"], request.form["video"], str([request.form['onename'], int(request.form['oneprice']), request.form['onestock']]), str([request.form['twoname'], int(request.form['twoprice']), request.form['twostock']]), str([request.form['threename'], int(request.form['threeprice']), request.form['threestock']]), request.form["id"]))
                                            con.commit()
                                            con.close()
                                            # laststock = len(request.form["stock"].split("\n"))
                                            # print (laststock)
                                            # if (prod_info[5] == ""):
                                            #     if (request.form["onestock"] != ""):
                                            #         server_info = get_info(name)
                                            #         if (server_info[20] != None):
                                            #             try:
                                            #                 if (name == "dench"):
                                            #                     names = request.form["name"]
                                            #                     webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[20])
                                            #                     embed = DiscordEmbed(title="자판기 바로가기", url=f"http://SA NC/{name}/shop", description=f"**제품이름**\n{names}\n**제품가격**\n{prod_info[3]}원\n**입고전 재고 갯수**\n0\n**입고된 재고 갯수**\n{laststock}개\n**남은 재고**\n{laststock}개", color=0x010101)
                                            #                     embed.set_author(name="입고알림", icon_url=prod_info[4])
                                            #                     embed.set_thumbnail(url=prod_info[4])
                                            #                     embed.set_footer(text=datetime.datetime.now().strftime('%m월 %d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode('unicode-escape'))
                                            #                     webhook.add_embed(embed)
                                            #                     webhook.execute()
                                            #                 else:
                                            #                     names = request.form["name"]
                                            #                     webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[20])
                                            #                     embed = DiscordEmbed(title="자판기 바로가기", url=f"http://SA NC/{name}/shop", description=f"**제품이름**\n{names}\n**제품가격**\n{prod_info[3]}원\n**입고전 재고 갯수**\n0\n**입고된 재고 갯수**\n{laststock}개\n**남은 재고**\n{laststock}개", color=0x010101)
                                            #                     embed.set_author(name="입고알림", icon_url=prod_info[4])
                                            #                     embed.set_thumbnail(url=prod_info[4])
                                            #                     embed.set_footer(text=datetime.datetime.now().strftime('%m월 %d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode('unicode-escape'))
                                            #                     webhook.add_embed(embed)
                                            #                     webhook.execute()
                                            #             except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                                            #                 print('예외가 발생했습니다.', e)
                                            #     return "ok"
                                            # if (prod_info[5] != ""):
                                            #     if (laststock > nowstock):
                                            #         server_info = get_info(name)
                                            #         if (server_info[20] != None):
                                            #             try:
                                            #                 if (name == "dench"):
                                            #                     names = request.form["name"]
                                            #                     webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[20])
                                            #                     embed = DiscordEmbed(title="자판기 바로가기", url=f"http://SA NC/{name}/shop", description=f"**제품이름**\n{names}\n**제품가격**\n{prod_info[3]}원\n**입고전 재고 갯수**\n{nowstock}\n**입고된 재고 갯수**\n{laststock - nowstock}개\n**남은 재고**\n{laststock}개", color=0x010101)
                                            #                     embed.set_author(name="입고알림", icon_url=prod_info[4])
                                            #                     embed.set_thumbnail(url=prod_info[4])
                                            #                     embed.set_footer(text=datetime.datetime.now().strftime('%m월 %d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode('unicode-escape'))
                                            #                     webhook.add_embed(embed)
                                            #                     webhook.execute()
                                            #                 else:
                                            #                     names = request.form["name"]
                                            #                     webhook = DiscordWebhook(username="SA NC Service", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url=server_info[20])
                                            #                     embed = DiscordEmbed(title="자판기 바로가기", url=f"http://SA NC/{name}/shop", description=f"**제품이름**\n{names}\n**제품가격**\n{prod_info[3]}원\n**입고전 재고 갯수**\n{nowstock}\n**입고된 재고 갯수**\n{laststock - nowstock}개\n**남은 재고**\n{laststock}개", color=0x010101)
                                            #                     embed.set_author(name="입고알림", icon_url=prod_info[4])
                                            #                     embed.set_thumbnail(url=prod_info[4])
                                            #                     embed.set_footer(text=datetime.datetime.now().strftime('%m월 %d일 %H시 %M분'.encode('unicode-escape').decode()).encode().decode('unicode-escape'))
                                            #                     webhook.add_embed(embed)
                                            #                     webhook.execute()
                                            #             except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                                            #                 print('예외가 발생했습니다.', e)
                                            return "ok"
                                        else:
                                            return "1원~1000만원까지만 판매 가능합니다."
                                    else:
                                        return "잘못된 접근입니다."
                                else:
                                    return "잘못된 접근입니다."
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)


@app.route("/admin/delete_product", subdomain='<name>', methods=["POST"])
def delete_product(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        if ("id" in request.form):
                            prod_info = search_prod(name, request.form["id"])
                            if (prod_info != None):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("DELETE FROM products WHERE id == ?",(request.form["id"],))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    return "잘못된 접근입니다."
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/log", subdomain='<name>', methods=["GET"])
def viewlog(name):
    if (request.method == "GET"):
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        server_info = get_info(name)
                        buylog = ast.literal_eval(server_info[4])
                        chargelog = ast.literal_eval(server_info[5])
                        return render_template("admin_log.html", buylog=buylog, chargelog=chargelog, server_info=server_info)
                    else:
                        return redirect("../shop")
                else:
                    return redirect("../shop")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/managereq", subdomain='<name>', methods=["GET", "POST"])
def managereq(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                if (name in session):
                    user_info = search_user(name, session[name])
                    if (user_info[5] == 1):
                        server_info = get_info(name)
                        if (server_info[13] == 1):
                            if (request.method == "GET"):
                                con = sqlite3.connect(db(name))
                                cur = con.cursor()
                                cur.execute("SELECT * FROM bankwait;")
                                reqs = cur.fetchall()
                                con.close()
                                return render_template("admin_managereq.html", server_info=server_info, reqs=reqs)
                            else:
                                if ("type" in request.get_json() and "id" in request.get_json() and request.get_json()["type"] in ["delete", "accept"]):
                                    con = sqlite3.connect(db(name))
                                    cur = con.cursor()
                                    if (request.get_json()["type"] == "delete"):
                                        cur.execute("DELETE FROM bankwait WHERE id == ?;", (request.get_json()["id"],))
                                        con.commit()
                                        con.close()
                                        return "ok"
                                    else:
                                        cur.execute("SELECT * FROM bankwait WHERE id == ?;", (request.get_json()["id"],))
                                        bankwait_info = cur.fetchone()
                                        if (bankwait_info == None):
                                            con.close()
                                            return "존재하지 않는 충전신청 입니다."
                                        else:
                                            cur.execute("UPDATE users SET money = money + ? WHERE id == ?;", (bankwait_info[2], request.get_json()["id"]))
                                            con.commit()
                                            cur.execute("DELETE FROM bankwait WHERE id == ?;", (request.get_json()["id"],))
                                            con.commit()
                                            con.close()
                                            return "ok"
                        else:
                            abort(404)
                    else:
                        return redirect("../shop")
                else:
                    return redirect("../shop")
            else:
                abort(404)
        else:
            abort(404)

@app.route("/admin/license", subdomain='<name>', methods=["GET", "POST"])
def manage_license(name):
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        return redirect("/ban")
    else:
        if (request.method == "GET"):
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            server_info = get_info(name)
                            if (is_expired(server_info[7])):
                                return render_template("admin_license.html", expire="0일 0시간 (만료됨)", server_info=server_info)
                            else:
                                return render_template("admin_license.html", expire=get_expiretime(server_info[7]), server_info=server_info)
                        else:
                            return redirect("../shop")
                    else:
                        return redirect("../shop")
                else:
                    abort(404)
            else:
                abort(404)
        
        else:
            if (name.isalpha()):
                if (os.path.isfile(db(name))):
                    if (name in session):
                        user_info = search_user(name, session[name])
                        if (user_info[5] == 1):
                            if ("code" in request.form and "confirm" in request.form):
                                license_key = request.form["code"]
                                con = sqlite3.connect(cwdir + "license.db")
                                server_info = get_info(name)
                                with con:
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM license WHERE code == ?;", (request.form["code"],))
                                    license_result = cur.fetchone()
                                    if (license_result != None):
                                        if (license_result[2] == ""):
                                            if (server_info[13] != license_result[5] and request.form["confirm"] == "0"):
                                                return "confirm_changetype"
                                            cur.execute("UPDATE license SET usedat = ?, usedip = ?, usedurl = ? WHERE code == ?;", (nowstr(), getip(), name, request.form["code"]))
                                            con.commit()
                                con.close()
                                if (license_result == None):
                                    return "존재하지 않는 라이센스입니다."
                                if (license_result[2] != ""):
                                    return "이미 사용된 라이센스입니다."

                                if (is_expired(server_info[7]) or server_info[13] != license_result[5]):
                                    now_expiretime = make_expiretime(license_result[1])
                                else:
                                    now_expiretime = add_time(server_info[7], license_result[1])

                                con = sqlite3.connect(db(name))
                                with con:
                                    cur = con.cursor()
                                    if (server_info[13] == license_result[5]):
                                        cur.execute("UPDATE info SET expiredate = ?;", (now_expiretime,))
                                        con.commit()
                                    else:
                                        cur.execute("UPDATE info SET expiredate = ?, type = ?;", (now_expiretime, license_result[5]))
                                        con.commit()
                                con.close()
                                if (server_info[13] == license_result[5]):
                                    return "ok|" + str(license_result[1]) + "|" + str(get_expiretime(now_expiretime))
                                else:
                                    return "ok|" + str(license_result[1]) + "|" + str(get_expiretime(now_expiretime)) + "|" + ("계좌 & 문화상품권 자동충전" if license_result[5] == 1 else "문화상품권 자동충전")
                            else:
                                return "잘못된 접근입니다."
                        else:
                            return "잘못된 접근입니다."
                    else:
                        return "잘못된 접근입니다."
                else:
                    abort(404)
            else:
                abort(404)

@app.route("/banklogin", methods=["POST"])
def banklogin():
    if ("id" in request.get_json() and "pw" in request.get_json()):
        name = request.get_json()["id"]
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                con = sqlite3.connect(db(name))
                cur = con.cursor()
                cur.execute("SELECT * FROM info;")
                shop_info = cur.fetchone()
                password = shop_info[12]
                con.close()
                if (password != "" and password == request.get_json()["pw"]):
                    return jsonify({"result": True, "reason" : "로그인 성공"})
                else:
                    return jsonify({"result": False, "reason" : "비밀번호가 틀렸습니다."})
            else:
                return jsonify({"result": False, "reason" : "로그인 실패"})
        else:
            return jsonify({"result": False, "reason" : "로그인 실패"})
    else:
        abort(400)


@app.route("/bankpost" ,methods=["POST"])
def bankpost():
    if ("amount" in request.json and "id" in request.json and "name" in request.json and "pw" in request.json):
        name = request.get_json()["id"]
        if (name.isalpha()):
            if (os.path.isfile(db(name))):
                con = sqlite3.connect(db(name))
                with con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM info;")
                    shop_info = cur.fetchone()
                    password = shop_info[12]
                    if (password != "" and password == request.get_json()["pw"]):
                        def process_post(name, amount, url):
                            print(f"[!] BANK POST ALERT : {name}, {amount} KRW")
                            cur.execute("SELECT * FROM bankwait WHERE name == ? AND amount == ?;", (name, amount))
                            chargeinfo_detail = cur.fetchone()
                            if (chargeinfo_detail != None):
                                print(f"[!] BANK POST complete : {name}, {amount} KRW")
                                webhook = DiscordWebhook(username="SA NC Web", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url="https://discord.com/api/webhooks/842029711981936681/K9lB4iAGbEruwgfPi_b0QUPm2uVcKrXWC2q12hvu7MNNqTsIvgX1W_TgcWwwRQkBdXz9")
                                embed = DiscordEmbed(description=f"[!] BANK POST complete : {name}, {amount} KRW", color=0xfc0a0a)
                                webhook.add_embed(embed)
                                webhook.execute()
                                cur.execute("UPDATE users SET money = money + ? WHERE id == ?;", (chargeinfo_detail[2], chargeinfo_detail[0]))
                                con.commit()
                                chargelog = ast.literal_eval(shop_info[5])
                                chargelog.append([nowstr(), chargeinfo_detail[0], name, "자동충전 완료", str(amount)])
                                cur.execute("UPDATE info SET chargelog = ?", (str(chargelog),))
                                con.commit()
                                cur.execute("DELETE FROM bankwait WHERE id == ?;", (chargeinfo_detail[0],))
                                con.commit()
                                return jsonify({"result": True, "reason" : "자동충전 성공"})
                            else:
                                return jsonify({"result": True, "reason" : "자동충전 실패"})

                        webhook = DiscordWebhook(username="SA NC Web", avatar_url="https://cdn.discordapp.com/attachments/969974533152968714/970969359671513108/sv_logo_2.png", url="https://discord.com/api/webhooks/842029711981936681/K9lB4iAGbEruwgfPi_b0QUPm2uVcKrXWC2q12hvu7MNNqTsIvgX1W_TgcWwwRQkBdXz9")
                        embed = DiscordEmbed(description=f"[!] BANK POST : {str(request.get_json())}", color=0xfc0a0a)
                        webhook.add_embed(embed)
                        webhook.execute()
                        print(f"[!] BANK POST : {str(request.get_json())}")

                        # 농협 계좌 입금시
                        if ("농협 입금" in request.json["name"] and "NH스마트알림" in request.json["name"]):
                            amount = request.json["name"].split("농협 입금")[1].split("원")[0].replace(",", "")
                            name = request.json["name"].split(" 잔액")[0].split(" ")[5]
                            return (process_post(name, amount, request.json["id"]))
                        #카뱅 계좌 입금시
                        elif ("입출금내역 안내" in request.json["name"] and "입금" in request.json["name"]):
                            name = request.json["name"].split(" ")
                            name = list(reversed(name))[0]
                            amount = request.json["name"].split("입금 ")[1].split(" ")[0].replace(",", "").replace("원", "")
                            return (process_post(name, amount, request.json["id"]))
                        #KB스타 계좌 입금시
                        elif ("KB스타알림" in request.json["name"] and "전자금융입금" in request.json["name"]):
                            amount = request.json["name"].split("전자금융입금")[1].split("원")[0].replace(",", "")
                            name = request.json["name"].split(" ")[3].split(" ")[0]
                            return (process_post(name, amount, request.json["id"]))
                        #케이뱅크 (기업) 계좌 입금시
                        elif ("케이뱅크" in request.json["name"] and "입금" in request.json["name"]):
                            name = request.json["name"].split("\n")[1].split(" ")[0]
                            amount = request.json["name"].split(" ")[2].split("\n")[0].replace(",", "").replace("원", "")
                            return (process_post(name, amount, request.json["id"]))
                        #하나은행 계좌 입금시
                        elif ("하나은행" in request.json["name"] and "입금" in request.json["name"]):
                            name = request.json["name"].split(" ")[1]
                            amount = request.json["name"].split(" ")[3].replace(",","").replace("원", "")
                            return (process_post(name, amount, request.json["id"]))
                        #신한은행 계좌 입금시
                        elif ("SOL알리미" in request.json["name"] and "입금" in request.json["name"]):
                            name = request.json["name"].split(" ")[3]
                            amount = request.json["name"].split(" ")[2].replace(",","").replace("원", "")
                            return (process_post(name, amount, request.json["id"]))
                        else:
                            return jsonify({"result": True, "reason" : "미지원 은행"})
                    else:
                        con.close()
                        return jsonify({"result": False, "reason" : "비밀번호가 틀렸습니다."})
            else:
                return jsonify({"result": False, "reason" : "로그인 실패"})
        else:
            return jsonify({"result": False, "reason" : "로그인 실패"})
    else:
        abort(400)

@app.route("/codepanel", methods=["GET", "POST"])
def codepanel():
    if (request.method == "GET"):
        return render_template("login.html", name="관리자 패널")
    else:
        if ("id" in request.form and "pw" in request.form):
            if (request.form["id"] in panel_keypair):
                if (panel_keypair[request.form["id"]] == request.form["pw"]):
                    session["codepanelsession"] = request.form["id"]
                    return redirect("generate")
                else:
                    return "Login Failed."
            else:
                return "Login Failed."
        else:
            return "Login Failed."

@app.route("/generate", methods=["GET", "POST"])
def gen():
    if ("codepanelsession" in session):
        if (request.method == "GET"):
            return render_template("codegen.html")
        else:
            if ("amount" in request.form and "days" in request.form and "options" in request.form):
                if (request.form["amount"].isdigit() and request.form["amount"] != "0" and request.form["days"] in ["1", "7", "30", "60", "90", "9999"] and request.form["options"] in ["moonsang", "full"]):
                    con = sqlite3.connect(f"{cwdir}license.db")
                    with con:
                        cur = con.cursor()
                        gened_codes = []
                        for n in range(int(request.form["amount"])):
                            generated = f"SANC-{randomstring.pick(20)}"
                            amount = int(request.form["amount"])
                            days = int(request.form["days"])
                            cur.execute("INSERT INTO license VALUES (?, ?, ?, ?, ?, ?);", (generated, int(request.form["days"]), "", "", "", 0 if request.form["options"] == "moonsang" else 1))
                            con.commit()
                            gened_codes.append(generated)
                        return "OK\n" + "\n".join(gened_codes)
                    con.close()
                else:
                    return "개수는 양수 및 정수만 허용됩니다."
            else:
                return "FUCK YOU ATTACKER"
    else:
        return redirect("http://warning.or.kr")

@app.route("/managekey", methods=["GET", "POST"])
def managekey():
    if ("codepanelsession" in session):
        if (request.method == "GET"):
            con = sqlite3.connect(f"{cwdir}license.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM license;")
            keys = cur.fetchall()
            con.close()
            return render_template("managekey.html", code_list=keys)
        else:
            if ("code" in request.get_json()):
                code = request.get_json()["code"]
                con = sqlite3.connect(f"{cwdir}license.db")
                cur = con.cursor()
                cur.execute("DELETE FROM license WHERE code == ?;", (code,))
                con.commit()
                con.close()
                return "OK"
            else:
                return "FUCK YOU ATTACKER"
    else:
        return redirect("http://warning.or.kr")

@app.route("/managestore", methods=["GET", "POST"])
def managestore():
    if ("codepanelsession" in session):
        if (request.method == "GET"):
            store_list = os.listdir(f"{cwdir}/database")
            return render_template("managestore.html", store_list=store_list)
        else:
            if ("code" in request.get_json()):
                code = request.get_json()["code"]
                try:
                    os.remove(f"{cwdir}/database/{code}")
                except:
                    return "Unknown Store"
                return "OK"
            else:
                return "FUCK YOU ATTACKER"
    else:
        return redirect("http://warning.or.kr")

@app.route("/logout", subdomain='<name>', methods=["GET"])
def logout(name):
    session.pop(name, None)
    return redirect("../login")

@app.route("/logout", methods=["GET"])
def logoutpanel(name):
    session.pop("codepanelsession", None)
    return redirect("../login")

@app.route("/ban", subdomain='<name>', methods=["GET"])
def ban(name):
    session.pop(name, None)    
    con = sqlite3.connect(f"{cwdir}ban.db")
    cur = con.cursor()
    cur.execute("SELECT EXISTS(SELECT * FROM ban WHERE ip == ?)", ([getip()]))
    found, = cur.fetchone()
    if found:
        con.close()
        pass
    else:
        cur.execute("INSERT INTO ban VALUES (?)", ([getip()]))
        con.commit()
        con.close()
    return render_template("ban.html", ip=getip())


# @app.before_request
# def make_session_permanent():
#     #if not ("SA NC" in request.headers["host"]):
#     #    return """<html>
#     #    <head><title>404 Not Found</title></head>
#     #    <body>
#     #    <center><h1>404 Not Found</h1></center>
#     #    <hr><center>nginx/1.19.9</center>
#     #    </body>
#     #    </html>"""
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=60)

#     ServerClosed = False

#     if (ServerClosed):
#         return render_template("서버점검.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

@app.errorhandler(500)
def server_crash_error(error):
    return render_template("500.html")    

app.run(host='0.0.0.0', port=80) # 
