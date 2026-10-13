import re
from django import template

register = template.Library()

# Kerala destinations, grouped by district. Add or remove names freely.
PLACES = [
    # ---------- Thiruvananthapuram ----------
    "Thiruvananthapuram", "Trivandrum", "Kovalam", "Varkala", "Poovar",
    "Ponmudi", "Neyyar", "Neyyar Dam", "Agasthyakoodam", "Vizhinjam",
    "Shanghumugham", "Veli", "Akkulam", "Kappil", "Anchuthengu", "Napier Museum",
    "Padmanabhaswamy", "Attukal", "Peppara", "Kanakakunnu", "Chembakkara",

    # ---------- Kollam ----------
    "Kollam", "Quilon", "Ashtamudi", "Thenmala", "Munroe Island", "Palaruvi",
    "Jatayu Earth's Center", "Jatayu", "Thangassery", "Paravur", "Kulathupuzha",
    "Aryankavu", "Achankovil", "Mayyanad", "Ochira", "Sasthamkotta", "Rosemala",

    # ---------- Pathanamthitta ----------
    "Pathanamthitta", "Sabarimala", "Gavi", "Konni", "Aranmula", "Perunthenaruvi",
    "Adoor", "Ranni", "Thiruvalla", "Pandalam", "Kakki", "Charalkunnu",

    # ---------- Alappuzha ----------
    "Alappuzha", "Alleppey", "Kuttanad", "Kumarakom", "Marari", "Mararikulam",
    "Punnamada", "Pathiramanal", "Arookutty", "Mannarasala", "Ambalappuzha",
    "Chettikulangara", "Thottappally", "Kayamkulam", "Haripad", "Chengannur",

    # ---------- Kottayam ----------
    "Kottayam", "Vagamon", "Ilaveezhapoonchira", "Illikkal Kallu", "Aruvikkuzhi",
    "Vaikom", "Kumarakom Bird Sanctuary", "Ettumanoor", "Bharananganam",
    "Meenachil", "Kurisumala", "Paruthumpara", "Thangalpara", "Erattupetta",

    # ---------- Idukki ----------
    "Idukki", "Munnar", "Thekkady", "Periyar", "Periyar Tiger Reserve",
    "Vandanmedu", "Kumily", "Marayoor", "Chinnar", "Eravikulam", "Anamudi",
    "Mattupetty", "Echo Point", "Top Station", "Rajamala", "Devikulam",
    "Chithirapuram", "Anayirankal", "Ponmudi Dam", "Kolukkumalai", "Meesapulimala",
    "Peermede", "Ramakkalmedu", "Kalvary Mount", "Cheeyappara", "Valara",
    "Thommankuthu", "Idukki Dam", "Kanthalloor", "Vattavada", "Pallivasal",
    "Elappara", "Santhanpara", "Chinnakanal", "Mankulam", "Adimali",

    # ---------- Ernakulam ----------
    "Ernakulam", "Kochi", "Cochin", "Fort Kochi", "Fort Cochin", "Mattancherry",
    "Marine Drive", "Bolgatty", "Willingdon Island", "Cherai", "Kuzhupilly",
    "Munambam", "Thattekad", "Bhoothathankettu", "Kothamangalam", "Muziris",
    "Kodanad", "Muvattupuzha", "Perumbavoor", "Aluva", "Vypin", "Chendamangalam",
    "Hill Palace", "Thripunithura", "Paniyeli Poru", "Malayattoor", "Neriamangalam",

    # ---------- Thrissur ----------
    "Thrissur", "Trichur", "Athirappilly", "Athirapally", "Vazhachal", "Charpa",
    "Guruvayur", "Chavakkad", "Snehatheeram", "Peechi", "Vazhani", "Shornur",
    "Kodungallur", "Chetuva", "Kerala Kalamandalam", "Cheruthuruthy", "Punnathur Kotta",
    "Thumboormuzhi", "Poomala", "Vilangan", "Vadakkunnathan",

    # ---------- Palakkad ----------
    "Palakkad", "Palghat", "Nelliyampathy", "Silent Valley", "Malampuzha",
    "Parambikulam", "Mangalam Dam", "Meenvallam", "Dhoni", "Kollengode",
    "Pothundi", "Siruvani", "Attappadi", "Mayiladumpara", "Kalpathy",
    "Palakkad Fort", "Seethargundu", "Chulannur", "Mukkali", "Tenmala Dam",

    # ---------- Malappuram ----------
    "Malappuram", "Nilambur", "Kottakkal", "Tirur", "Ponnani", "Kadalundi",
    "Thirunavaya", "Biyyam Kayal", "Manjeri", "Perinthalmanna", "Angadipuram",
    "Conolly Plot", "Aruvacode", "Kottakunnu",

    # ---------- Kozhikode ----------
    "Kozhikode", "Calicut", "Kappad", "Beypore", "Kakkayam", "Thusharagiri",
    "Tusharagiri", "Peruvannamuzhi", "Payyoli", "Vadakara", "Iringal",
    "Sargaalaya", "Mananchira", "Thamarassery", "Kuttiyadi", "Jankey",
    "Kozhippara", "Arippara", "Velliyamkallu",

    # ---------- Wayanad ----------
    "Wayanad", "Vythiri", "Lakkidi", "Edakkal", "Edakkal Caves", "Banasura",
    "Banasura Sagar", "Kalpetta", "Sulthan Bathery", "Sultan Bathery", "Mananthavady",
    "Pookode", "Pookode Lake", "Chembra", "Chembra Peak", "Soochipara", "Sentinel Rock",
    "Meenmutty", "Kuruva", "Kuruvadweep", "Tholpetty", "Muthanga", "Neelimala",
    "Thirunelli", "Pakshipathalam", "Phantom Rock", "Karlad", "Kanthanpara",
    "Chain Tree", "Ambalavayal", "Padinjarathara", "Kabini",

    # ---------- Kannur ----------
    "Kannur", "Cannanore", "Muzhappilangad", "Payyambalam", "Parassinikadavu",
    "Aralam", "Dharmadam", "Meenkunnu", "St. Angelo", "Arakkal", "Madayipara",
    "Palakkayam Thattu", "Kannur Fort", "Thalassery", "Thalassery Fort",
    "Ezhimala", "Valapattanam", "Pazhassi Dam", "Paithalmala", "Kottiyoor",
    "Sreekandapuram", "Kakkadampoyil", "Peralassery", "Cherukunnu",

    # ---------- Kasaragod ----------
    "Kasaragod", "Bekal", "Bekal Fort", "Ranipuram", "Valiyaparamba", "Kappil Beach",
    "Chandragiri", "Chandragiri Fort", "Thirumala", "Nileshwar", "Kanhangad",
    "Madhur", "Ananthapura", "Bela", "Hosdurg", "Poinachi", "Kottancheri",
    "Malik Dinar", "Kumbla", "Manjeshwar", "Trikaripur",
]

# Longest names first, so "Fort Kochi" is preferred over "Kochi" when both
# match at the same position.
_PLACES_SORTED = sorted(set(PLACES), key=len, reverse=True)
_PLACES_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in _PLACES_SORTED) + r")\b",
    re.I,
)


@register.filter
def extract_location(text):
    """
    1) 'Location: xxx' / 'Destination: xxx' / 'Place: xxx' line, if present.
    2) Otherwise the first Kerala destination mentioned in the text,
       returned as 'Place, Kerala'.
    """
    if not text:
        return ""

    text = str(text)
    text = re.sub(r"</(p|div|li|h[1-6])>|<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")

    # 1) explicit label
    m = re.search(r"(?:Location|Destination|Place)\s*[:\-–]\s*([^\n.;|]+)", text, re.I)
    if m:
        return m.group(1).strip()

    # 2) first known place mentioned
    pm = _PLACES_RE.search(text)
    if pm:
        # use the spelling from the PLACES list (fixes capitalisation)
        found = next((p for p in _PLACES_SORTED if p.lower() == pm.group(1).lower()), pm.group(1))
        return found + ", Kerala"
    return ""