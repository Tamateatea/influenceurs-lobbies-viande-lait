import json, re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get(url, timeout=30):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except Exception:
        return ""

def channel_id(handle):
    h = get(f"https://www.youtube.com/@{handle}")
    ids = re.findall(r"(UC[A-Za-z0-9_-]{22})", h)
    if not ids:
        return None
    return max(set(ids), key=ids.count)

def videos(cid, n=15):
    x = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    ids = re.findall(r"<yt:videoId>([\w-]{11})</yt:videoId>", x)
    titles = re.findall(r"<media:title>(.*?)</media:title>", x)
    return list(zip(ids, titles + [""] * len(ids)))[:n]

def declared(vid):
    return "paidContentOverlayRenderer" in get(f"https://www.youtube.com/watch?v={vid}")

def sponsorblock(vid):
    r = get(f"https://sponsor.ajay.app/api/skipSegments?videoID={vid}&category=sponsor", 20)
    try:
        return len(json.loads(r))
    except Exception:
        return 0

HANDLES = ["Squeezie", "MisterV", "Inoxtag", "Valouzz", "lorisgiuliano", "McFlyetCarlito"]

print(f"{'CHAINE':16s} {'VIDEO':13s} {'DECLARE':>8s} {'SPONSORBLOCK':>13s}  TITRE")
tot = {"both": 0, "decl_only": 0, "sb_only": 0, "none": 0}
for h in HANDLES:
    cid = channel_id(h)
    if not cid:
        print(f"{h:16s} -- chaine introuvable")
        continue
    vids = videos(cid)
    with ThreadPoolExecutor(8) as ex:
        decls = list(ex.map(lambda v: declared(v[0]), vids))
        sbs = list(ex.map(lambda v: sponsorblock(v[0]), vids))
    for (vid, title), d, s in zip(vids, decls, sbs):
        key = "both" if d and s else "decl_only" if d else "sb_only" if s else "none"
        tot[key] += 1
        if d or s:
            print(f"{h:16s} {vid:13s} {'OUI' if d else 'non':>8s} {s:>13d}  {title[:44]}")

print()
print("TABLEAU CROISE sur", sum(tot.values()), "videos")
print(f"  declare ET SponsorBlock      : {tot['both']}")
print(f"  declare SEUL                 : {tot['decl_only']}")
print(f"  SponsorBlock SEUL (non declare!) : {tot['sb_only']}")
print(f"  aucun des deux               : {tot['none']}")
