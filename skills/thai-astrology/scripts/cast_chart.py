#!/usr/bin/env python3
"""ผูกดวงโหราศาสตร์ไทย ใช้ Swiss Ephemeris คำนวณตำแหน่งดาว 10 ดวง + ลัคนา + ภพ 12

Usage:
    python cast_chart.py --date 2535-01-15 --time 08:30 --place กรุงเทพ
    python cast_chart.py --date 2535-01-15 --time 08:30 --lat 13.7563 --lon 100.5018
    python cast_chart.py --date 1992-01-15 --time 08:30 --place bangkok --ayanamsa lahiri
"""
import argparse
import json
import sys

try:
    import swisseph as swe
except ImportError:
    print("ERROR: ต้องติดตั้ง pyswisseph ก่อน → pip install pyswisseph", file=sys.stderr)
    sys.exit(1)


# พิกัดเมืองหลักของไทย (ละติจูด, ลองจิจูด)
THAI_CITIES = {
    "กรุงเทพ": (13.7563, 100.5018),
    "bangkok": (13.7563, 100.5018),
    "เชียงใหม่": (18.7883, 98.9853),
    "เชียงราย": (19.9105, 99.8406),
    "ขอนแก่น": (16.4419, 102.8359),
    "นครราชสีมา": (14.9799, 102.0978),
    "อุดรธานี": (17.4138, 102.7872),
    "ภูเก็ต": (7.8804, 98.3923),
    "สงขลา": (7.1899, 100.5954),
    "ชลบุรี": (13.3611, 100.9847),
    "นนทบุรี": (13.8622, 100.5134),
    "ปทุมธานี": (14.0208, 100.5250),
    "พิษณุโลก": (16.8298, 100.2654),
    "นครสวรรค์": (15.7047, 100.1372),
    "อยุธยา": (14.3692, 100.5876),
    "กระบี่": (8.0863, 98.9063),
    "กาญจนบุรี": (14.0228, 99.5328),
    "กาฬสินธุ์": (16.4385, 103.5061),
    "กำแพงเพชร": (16.4828, 99.5227),
    "จันทบุรี": (12.6113, 102.1038),
    "ฉะเชิงเทรา": (13.6904, 101.0779),
    "ชัยนาท": (15.1852, 100.1251),
    "ชัยภูมิ": (15.8068, 102.0315),
    "ชุมพร": (10.4930, 99.1800),
    "ตรัง": (7.5594, 99.6114),
    "ตราด": (12.2428, 102.5175),
    "ตาก": (16.8839, 99.1258),
    "นครนายก": (14.2069, 101.2131),
    "นครปฐม": (13.8199, 100.0622),
    "นครพนม": (17.3920, 104.7696),
    "นครศรีธรรมราช": (8.4304, 99.9631),
    "นราธิวาส": (6.4255, 101.8253),
    "น่าน": (18.7883, 100.7760),
    "บึงกาฬ": (18.3609, 103.6464),
    "บุรีรัมย์": (14.9930, 103.1029),
    "ประจวบคีรีขันธ์": (11.8124, 99.7973),
    "ปราจีนบุรี": (14.0509, 101.3727),
    "ปัตตานี": (6.8695, 101.2505),
    "พะเยา": (19.1665, 99.9019),
    "พังงา": (8.4501, 98.5255),
    "พัทลุง": (7.6167, 100.0740),
    "พิจิตร": (16.4419, 100.3488),
    "เพชรบุรี": (13.1119, 99.9447),
    "เพชรบูรณ์": (16.4190, 101.1606),
    "แพร่": (18.1446, 100.1403),
    "มหาสารคาม": (16.1851, 103.3026),
    "มุกดาหาร": (16.5453, 104.7235),
    "แม่ฮ่องสอน": (19.3020, 97.9654),
    "ยโสธร": (15.7926, 104.1453),
    "ยะลา": (6.5411, 101.2804),
    "ร้อยเอ็ด": (16.0538, 103.6520),
    "ระนอง": (9.9529, 98.6085),
    "ระยอง": (12.6814, 101.2816),
    "ราชบุรี": (13.5283, 99.8134),
    "ลพบุรี": (14.7995, 100.6534),
    "ลำปาง": (18.2888, 99.4909),
    "ลำพูน": (18.5745, 99.0087),
    "เลย": (17.4860, 101.7223),
    "ศรีสะเกษ": (15.1186, 104.3220),
    "สกลนคร": (17.1546, 104.1348),
    "สตูล": (6.6238, 100.0674),
    "สมุทรปราการ": (13.5991, 100.5998),
    "สมุทรสงคราม": (13.4098, 100.0023),
    "สมุทรสาคร": (13.5475, 100.2744),
    "สระแก้ว": (13.8240, 102.0646),
    "สระบุรี": (14.5289, 100.9101),
    "สิงห์บุรี": (14.8936, 100.3967),
    "สุโขทัย": (17.0078, 99.8230),
    "สุพรรณบุรี": (14.4745, 100.1177),
    "สุราษฎร์ธานี": (9.1382, 99.3215),
    "สุรินทร์": (14.8829, 103.4937),
    "หนองคาย": (17.8783, 102.7413),
    "หนองบัวลำภู": (17.2218, 102.4260),
    "อ่างทอง": (14.5896, 100.4551),
    "อำนาจเจริญ": (15.8657, 104.6258),
    "อุตรดิตถ์": (17.6201, 100.0993),
    "อุทัยธานี": (15.3835, 100.0246),
    "อุบลราชธานี": (15.2287, 104.8564),
    "พระนครศรีอยุธยา": (14.3692, 100.5876),
}

# ดาวพระเคราะห์ในระบบไทย (เลขไทย: ดาว, swe_id)
PLANETS_THAI = [
    ("๑", "อาทิตย์", swe.SUN),
    ("๒", "จันทร์", swe.MOON),
    ("๓", "อังคาร", swe.MARS),
    ("๔", "พุธ", swe.MERCURY),
    ("๕", "พฤหัสบดี", swe.JUPITER),
    ("๖", "ศุกร์", swe.VENUS),
    ("๗", "เสาร์", swe.SATURN),
    ("๘", "ราหู", swe.MEAN_NODE),  # จุดโหนดเฉลี่ย
    ("๐", "มฤตยู", swe.URANUS),
]

# ราศี 12 ราศี (ตามลำดับ 0-11)
RASI_NAMES = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
              "ตุล", "พิจิก", "ธนู", "มังกร", "กุมภ์", "มีน"]

# ดาวเกษตรประจำราศี (index ของ PLANETS_THAI ที่ครองราศีนั้น)
RASI_LORDS = {
    "เมษ": "อังคาร", "พฤษภ": "ศุกร์", "เมถุน": "พุธ", "กรกฎ": "จันทร์",
    "สิงห์": "อาทิตย์", "กันย์": "พุธ", "ตุล": "ศุกร์", "พิจิก": "อังคาร",
    "ธนู": "พฤหัสบดี", "มังกร": "เสาร์", "กุมภ์": "เสาร์", "มีน": "พฤหัสบดี"
}

# ตารางมาตรฐานดาว: เกษตร, อุจ(ราศี, องศา), นิจ(ราศี, องศา)
PLANET_STANDARDS = {
    "อาทิตย์":  {"เกษตร": ["สิงห์"], "อุจ": ("เมษ", 10), "นิจ": ("ตุล", 10)},
    "จันทร์":   {"เกษตร": ["กรกฎ"], "อุจ": ("พฤษภ", 3), "นิจ": ("พิจิก", 3)},
    "อังคาร":   {"เกษตร": ["เมษ", "พิจิก"], "อุจ": ("มังกร", 28), "นิจ": ("กรกฎ", 28)},
    "พุธ":       {"เกษตร": ["เมถุน", "กันย์"], "อุจ": ("กันย์", 15), "นิจ": ("มีน", 15)},
    "พฤหัสบดี": {"เกษตร": ["ธนู", "มีน"], "อุจ": ("กรกฎ", 5), "นิจ": ("มังกร", 5)},
    "ศุกร์":     {"เกษตร": ["พฤษภ", "ตุล"], "อุจ": ("มีน", 27), "นิจ": ("กันย์", 27)},
    "เสาร์":     {"เกษตร": ["มังกร", "กุมภ์"], "อุจ": ("ตุล", 20), "นิจ": ("เมษ", 20)},
}

# ชื่อภพ 12 ภพ
BHAVA_NAMES = ["ตนุ", "กฎุมพะ", "สหัชชะ", "พันธุ", "ปุตตะ", "อริ",
               "ปัตนิ", "มรณะ", "ศุภะ", "กัมมะ", "ลาภะ", "วินาสนะ"]


# ---------------------------------------------------------------------------
# นักษัตร 27 ฤกษ์ / 9 ชื่อฤกษ์ / เจ้าฤกษ์ / ตรียางค์
# ---------------------------------------------------------------------------

# นักษัตร 27 ดวง เรียงตามลำดับ (แต่ละดวงกว้าง 13°20')
NAKSHATRA_NAMES = [
    "อัศวินี", "ภรณี", "กฤติกา", "โรหิณี", "มฤคศิระ", "อารทรา", "ปุนัพสุ",
    "ปุษยะ", "อาศเลษา", "มฆา", "บุรพผลคุนี", "อุตรผลคุนี", "หัสตะ", "จิตรา",
    "สวาติ", "วิสาขะ", "อนุราธา", "เชษฐา", "มูละ", "บุรพาษาฒ", "อุตราษาฒ",
    "ศรวณะ", "ธนิษฐา", "ศตภิษัช", "บุรพภัทรบท", "อุตรภัทรบท", "เรวดี",
]

# ชื่อฤกษ์ 9 หมู่ วนซ้ำทุก 9 นักษัตร (นักษัตรที่ 1 = ทลิทโท)
RUEK_NAMES = [
    "ทลิทโท", "มหัทธโน", "โจโร", "ภูมิปาโล", "เทศาตรี",
    "เทวี", "เพชฌฆาต", "ราชา", "สมโณ",
]

# ความหมายย่อของแต่ละฤกษ์ (ใช้ประกอบการตีความ ไม่ใช่ผลคำนวณ)
RUEK_MEANINGS = {
    "ทลิทโท": "ผู้ใหญ่อุปถัมภ์ ตั้งตัวจากศูนย์ ขยันอดทน",
    "มหัทธโน": "ทรัพย์สิน การค้า มั่งคั่งจากความเพียร",
    "โจโร": "ช่วงชิง แข่งขัน กล้าเสี่ยง ต้องระวังการสูญเสีย",
    "ภูมิปาโล": "หลักฐานมั่นคง ที่ดิน บ้านเรือน คุ้มครองรักษา",
    "เทศาตรี": "พลัดถิ่น เคลื่อนไหว ทำหลายอย่าง ค้าขายต่างแดน",
    "เทวี": "เสน่ห์ ศิลปะ ความงาม เป็นที่รักของผู้คน",
    "เพชฌฆาต": "เด็ดขาด กล้าหาญ งานที่ต้องตัดสินใจแทนผู้อื่น",
    "ราชา": "อำนาจ เกียรติยศ ผู้นำ งานราชการ",
    "สมโณ": "สงบ สันโดษ วิชาความรู้ ธรรมะ",
}

# เจ้าฤกษ์ประจำนักษัตร วนซ้ำทุก 9 ดวง (ลำดับเดียวกับทศาวิมโศตตรี)
NAKSHATRA_LORDS = [
    "เกตุ", "ศุกร์", "อาทิตย์", "จันทร์", "อังคาร",
    "ราหู", "พฤหัสบดี", "เสาร์", "พุธ",
]


def nakshatra_info(longitude: float):
    """คืนข้อมูลฤกษ์ของลองจิจูดที่ให้มา (นักษัตร ชื่อฤกษ์ เจ้าฤกษ์ บาท ความคืบหน้า)"""
    longitude = longitude % 360
    span = 40.0 / 3.0  # 13°20'
    idx = int(longitude // span)
    into = longitude - idx * span
    remaining = span - into
    return {
        "นักษัตรที่": idx + 1,
        "นักษัตร": NAKSHATRA_NAMES[idx],
        "ฤกษ์": RUEK_NAMES[idx % 9],
        "เจ้าฤกษ์": NAKSHATRA_LORDS[idx % 9],
        "บาท": int(into // (span / 4)) + 1,
        "เดินไปแล้ว_%": round(into / span * 100, 1),
        "เหลืออีก_องศา": round(remaining, 3),
        "ฤกษ์ถัดไป": RUEK_NAMES[(idx + 1) % 9],
        "นักษัตรถัดไป": NAKSHATRA_NAMES[(idx + 1) % 27],
        "เจ้าฤกษ์ถัดไป": NAKSHATRA_LORDS[(idx + 1) % 9],
    }


def triyang_info(longitude: float):
    """คืนตรียางค์ (แบ่งราศีละ 3 ส่วน ส่วนละ 10 องศา) และเจ้าตรียางค์"""
    longitude = longitude % 360
    rasi_idx = int(longitude // 30)
    deg_in_rasi = longitude - rasi_idx * 30
    part = int(deg_in_rasi // 10)          # 0,1,2
    owner_idx = (rasi_idx + 4 * part) % 12  # ราศีเดิม → ที่ 5 → ที่ 9 (ธาตุเดียวกัน)
    owner_rasi = RASI_NAMES[owner_idx]
    return {
        "ตรียางค์ที่": part + 1,
        "ช่วงองศา": f"{part * 10}-{part * 10 + 10}",
        "ราศีตรียางค์": owner_rasi,
        "เจ้าตรียางค์": RASI_LORDS[owner_rasi],
    }


def tithi_info(sun_lon: float, moon_lon: float):
    """คืนดิถี (ขึ้น/แรม กี่ค่ำ) จากระยะห่างจันทร์-อาทิตย์ ค่านี้ไม่ขึ้นกับระบบราศี"""
    elong = (moon_lon - sun_lon) % 360
    tithi_no = int(elong // 12) + 1          # 1-30
    if tithi_no <= 15:
        phase, day = "ขึ้น", tithi_no
    else:
        phase, day = "แรม", tithi_no - 15
    illum = round((1 - __import__("math").cos(__import__("math").radians(elong))) / 2 * 100, 1)
    return {
        "ระยะจันทร์-อาทิตย์": round(elong, 2),
        "ดิถีที่": tithi_no,
        "ดิถี": f"{phase} {day} ค่ำ",
        "ส่วนสว่าง_%": illum,
    }


def parse_date_thai_or_western(date_str: str):
    """รับวันที่ในรูป YYYY-MM-DD โดยถ้า YYYY > 2400 ถือว่าเป็น พ.ศ. แล้วแปลงเป็น ค.ศ."""
    year, month, day = map(int, date_str.split("-"))
    if year > 2400:
        year -= 543  # แปลง พ.ศ. → ค.ศ.
    return year, month, day


def degrees_to_rasi(longitude: float):
    """แปลงองศาสุริยปฏิทิน (0-360) เป็น (ราศี, องศาในราศี)"""
    longitude = longitude % 360
    rasi_index = int(longitude // 30)
    deg_in_rasi = longitude - (rasi_index * 30)
    return RASI_NAMES[rasi_index], deg_in_rasi, rasi_index


def evaluate_standard(planet_name: str, rasi: str, deg_in_rasi: float):
    """ประเมินว่าดาวอยู่ในมาตรฐานใด (เกษตร/อุจ/มหาอุจ/นิจ/ประ/ปกติ)"""
    if planet_name not in PLANET_STANDARDS:
        return "—"
    std = PLANET_STANDARDS[planet_name]
    if rasi in std["เกษตร"]:
        return "เกษตร"
    uj_rasi, uj_deg = std["อุจ"]
    if rasi == uj_rasi:
        return "มหาอุจ" if abs(deg_in_rasi - uj_deg) < 1 else "อุจ"
    nij_rasi, _nij_deg = std["นิจ"]
    if rasi == nij_rasi:
        return "นิจ"
    # ปรเกษตร = ราศีตรงข้ามกับเกษตร
    rasi_idx = RASI_NAMES.index(rasi)
    opp_idx = (rasi_idx + 6) % 12
    opposite = RASI_NAMES[opp_idx]
    if opposite in std["เกษตร"]:
        return "ประ"
    return "ปกติ"


def cast_chart(date_str: str, time_str: str, lat: float, lon: float,
               ayanamsa: str = "tropical", tz_offset: float = 7.0,
               time_estimated: bool = False):
    """คำนวณดวงชะตา return dict พร้อมข้อมูลครบ"""
    year, month, day = parse_date_thai_or_western(date_str)
    hour, minute = map(int, time_str.split(":"))

    # คำนวณ Julian Day (UT)
    decimal_hour = hour + minute / 60.0 - tz_offset
    jd_ut = swe.julday(year, month, day, decimal_hour)

    # ตั้งค่า ayanamsa
    flags = swe.FLG_SPEED
    if ayanamsa.lower() == "lahiri":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags |= swe.FLG_SIDEREAL
    # ถ้า tropical ไม่ต้องตั้ง — เป็น default

    # คำนวณตำแหน่งดาว
    planets_out = []
    for thai_num, name, swe_id in PLANETS_THAI:
        result, _ = swe.calc_ut(jd_ut, swe_id, flags)
        lon_deg = result[0]
        rasi, deg_in_rasi, _ = degrees_to_rasi(lon_deg)
        standard = evaluate_standard(name, rasi, deg_in_rasi)
        planets_out.append({
            "เลข": thai_num,
            "ดาว": name,
            "ราศี": rasi,
            "องศา": round(deg_in_rasi, 2),
            "longitude": round(lon_deg, 4),
            "มาตรฐาน": standard,
            "ฤกษ์": nakshatra_info(lon_deg)["ฤกษ์"],
            "นักษัตร": nakshatra_info(lon_deg)["นักษัตร"],
        })

    # เกตุ = ตรงข้ามราหู
    rahu = planets_out[7]  # ราหู
    ketu_lon = (rahu["longitude"] + 180) % 360
    ketu_rasi, ketu_deg, _ = degrees_to_rasi(ketu_lon)
    planets_out.append({
        "เลข": "๙",
        "ดาว": "เกตุ",
        "ราศี": ketu_rasi,
        "องศา": round(ketu_deg, 2),
        "longitude": round(ketu_lon, 4),
        "มาตรฐาน": "—",
    })

    # คำนวณลัคนา (Ascendant)
    _houses, ascmc = swe.houses(jd_ut, lat, lon, b'P')  # Placidus
    lakkana_lon = ascmc[0]
    if ayanamsa.lower() == "lahiri":
        lakkana_lon = (lakkana_lon - swe.get_ayanamsa_ut(jd_ut)) % 360
    lakkana_rasi, lakkana_deg, lakkana_idx = degrees_to_rasi(lakkana_lon)
    lakkana_lord = RASI_LORDS[lakkana_rasi]

    # วางภพ 12 จากลัคนา
    bhava_map = {}
    for i in range(12):
        rasi_index = (lakkana_idx + i) % 12
        bhava_map[BHAVA_NAMES[i]] = {
            "ภพที่": i + 1,
            "ราศี": RASI_NAMES[rasi_index],
            "ดาวสถิต": [p["ดาว"] for p in planets_out if p["ราศี"] == RASI_NAMES[rasi_index]]
        }

    ayan_value = swe.get_ayanamsa_ut(jd_ut) if ayanamsa.lower() == "lahiri" else 0.0

    sun_lon = planets_out[0]["longitude"]
    moon_lon = planets_out[1]["longitude"]

    return {
        "ข้อมูลเกิด": {
            "วันเกิด_คศ": f"{year}-{month:02d}-{day:02d}",
            "เวลาเกิด": time_str,
            "เวลาเกิดเป็นค่าประมาณ": time_estimated,
            **({"หมายเหตุเวลาเกิด": (
                "ไม่ทราบเวลาเกิดจริง ใช้ค่าเริ่มต้น 06:00 น. (สมมุติพระอาทิตย์ขึ้น ตามธรรมเนียมสุริยยาตร์ไทย) "
                "ต่างจาก default 06:55 ของบางเครื่องมือ (เช่น myhora) ซึ่งพิสูจน์แล้วว่าให้ลัคนา/ฤกษ์คลาดเคลื่อน "
                "ลัคนาและภพที่คำนวณได้เป็นค่าประมาณ ใช้เวลาเกิดจริงถ้ามี"
            )} if time_estimated else {}),
            "ละติจูด": lat,
            "ลองจิจูด": lon,
            "ระบบ": "Sayana (Tropical)" if ayanamsa == "tropical" else "Nirayana (Lahiri)",
            "ayanamsa": round(ayan_value, 4),
            "julian_day_ut": round(jd_ut, 6),
        },
        "ลัคนา": {
            "ราศี": lakkana_rasi,
            "องศา": round(lakkana_deg, 2),
            "longitude": round(lakkana_lon, 4),
            "ดาวเจ้าเรือน(ลัคนาธิปติ)": lakkana_lord,
            "ฤกษ์": nakshatra_info(lakkana_lon),
            "ตรียางค์": triyang_info(lakkana_lon),
        },
        "ดิถี": tithi_info(sun_lon, moon_lon),
        "ดาว": planets_out,
        "ภพ": bhava_map
    }


# ---------------------------------------------------------------------------
# โหมดเทียบสองระบบ: สายนะ (Sayana/Tropical) vs นิรายนะ (Nirayana/Lahiri)
# ---------------------------------------------------------------------------

# อักขระไทยที่ไม่กินความกว้างเวลาแสดงผล (สระบน-ล่าง วรรณยุกต์)
_ZERO_WIDTH = set("ั") | set(chr(c) for c in range(0x0E34, 0x0E3B)) | \
              set(chr(c) for c in range(0x0E47, 0x0E4F))


def _w(text: str) -> int:
    """ความกว้างแสดงผลโดยประมาณ ไม่นับสระ/วรรณยุกต์ที่ซ้อนบนล่าง"""
    return sum(0 if ch in _ZERO_WIDTH else 1 for ch in str(text))


def _pad(text: str, width: int) -> str:
    text = str(text)
    return text + " " * max(0, width - _w(text))


def _asc_longitude(jd_ut: float, lat: float, lon: float) -> float:
    return swe.houses(jd_ut, lat, lon, b'P')[1][0]


def compare_charts(date_str: str, time_str: str, lat: float, lon: float,
                   tz_offset: float = 7.0, time_estimated: bool = False):
    """ผูกดวงทั้งสองระบบแล้วคืนโครงสร้างเปรียบเทียบ"""
    trop = cast_chart(date_str, time_str, lat, lon, "tropical", tz_offset, time_estimated)
    nira = cast_chart(date_str, time_str, lat, lon, "lahiri", tz_offset, time_estimated)

    jd_ut = trop["ข้อมูลเกิด"]["julian_day_ut"]
    ayan = nira["ข้อมูลเกิด"]["ayanamsa"]

    # อัตราลัคนาเดิน (องศา/นาที) จากผลต่าง 4 นาที — ใช้ได้กับทั้งสองระบบ
    a0 = _asc_longitude(jd_ut, lat, lon)
    a1 = _asc_longitude(jd_ut + 4.0 / 1440.0, lat, lon)
    rate = ((a1 - a0) % 360) / 4.0

    def boundary(chart):
        deg = chart["ลัคนา"]["องศา"]
        to_next = 30.0 - deg
        return {
            "องศาถึงเส้นแบ่งราศีถัดไป": round(to_next, 3),
            "นาทีของเวลาเกิด": round(to_next / rate, 1) if rate else None,
            "องศาจากเส้นแบ่งราศีก่อนหน้า": round(deg, 3),
            "นาทีจากเส้นแบ่งก่อนหน้า": round(deg / rate, 1) if rate else None,
        }

    def by_name(chart):
        return {p["ดาว"]: p for p in chart["ดาว"]}

    def bhava_of(chart):
        out = {}
        for bname, b in chart["ภพ"].items():
            for planet in b["ดาวสถิต"]:
                out[planet] = (b["ภพที่"], bname)
        return out

    tp, np_ = by_name(trop), by_name(nira)
    tb, nb = bhava_of(trop), bhava_of(nira)

    planets = []
    for name in [p["ดาว"] for p in trop["ดาว"]]:
        a, b = tp[name], np_[name]
        planets.append({
            "ดาว": name,
            "สายนะ": {"ราศี": a["ราศี"], "องศา": a["องศา"], "มาตรฐาน": a["มาตรฐาน"],
                       "ภพ": tb.get(name, (None, "—"))[0], "ชื่อภพ": tb.get(name, (None, "—"))[1]},
            "นิรายนะ": {"ราศี": b["ราศี"], "องศา": b["องศา"], "มาตรฐาน": b["มาตรฐาน"],
                         "ภพ": nb.get(name, (None, "—"))[0], "ชื่อภพ": nb.get(name, (None, "—"))[1]},
            "ต่างราศี": a["ราศี"] != b["ราศี"],
            "ต่างภพ": tb.get(name, (None,))[0] != nb.get(name, (None,))[0],
        })

    return {
        "ข้อมูลเกิด": {
            "วันเกิด_คศ": trop["ข้อมูลเกิด"]["วันเกิด_คศ"],
            "เวลาเกิด": time_str,
            "เวลาเกิดเป็นค่าประมาณ": time_estimated,
            **({"หมายเหตุเวลาเกิด": trop["ข้อมูลเกิด"]["หมายเหตุเวลาเกิด"]} if time_estimated else {}),
            "ละติจูด": lat,
            "ลองจิจูด": lon,
            "ayanamsa_Lahiri": ayan,
            "อัตราลัคนาเดิน_องศาต่อนาที": round(rate, 4),
        },
        "ลัคนา": {
            "สายนะ": {**trop["ลัคนา"], "ระยะถึงเส้นแบ่งราศี": boundary(trop)},
            "นิรายนะ": {**nira["ลัคนา"], "ระยะถึงเส้นแบ่งราศี": boundary(nira)},
            "ต่างราศี": trop["ลัคนา"]["ราศี"] != nira["ลัคนา"]["ราศี"],
        },
        "ดิถี": trop["ดิถี"],
        "ดาว": planets,
        "สรุปความต่าง": {
            "จำนวนดาวที่ต่างราศี": sum(1 for p in planets if p["ต่างราศี"]),
            "จำนวนดาวที่ต่างภพ": sum(1 for p in planets if p["ต่างภพ"]),
            "ลัคนาต่างราศี": trop["ลัคนา"]["ราศี"] != nira["ลัคนา"]["ราศี"],
        },
    }


def render_compare_text(c: dict) -> str:
    """แปลงผลเทียบเป็นตารางอ่านง่าย"""
    L, out = [], []
    b = c["ข้อมูลเกิด"]
    out.append("=" * 74)
    out.append(f"เทียบดวงสองระบบ  {b['วันเกิด_คศ']}  {b['เวลาเกิด']} น.  "
               f"({b['ละติจูด']}, {b['ลองจิจูด']})")
    out.append(f"ayanamsa Lahiri ณ วันเกิด = {b['ayanamsa_Lahiri']}°   "
               f"อัตราลัคนาเดิน {b['อัตราลัคนาเดิน_องศาต่อนาที']}°/นาที")
    if b.get("เวลาเกิดเป็นค่าประมาณ"):
        out.append(f"!! {b['หมายเหตุเวลาเกิด']}")
    out.append("=" * 74)

    s_, n_ = c["ลัคนา"]["สายนะ"], c["ลัคนา"]["นิรายนะ"]
    out.append("")
    out.append("── ลัคนา ──")
    out.append(f"  สายนะ (ทรอปิคัล) : {_pad(s_['ราศี'], 7)} {s_['องศา']:6.2f}°  "
               f"(สัมบูรณ์ {s_['longitude']:8.3f}°)  เจ้าเรือน {s_['ดาวเจ้าเรือน(ลัคนาธิปติ)']}")
    out.append(f"  นิรายนะ (Lahiri) : {_pad(n_['ราศี'], 7)} {n_['องศา']:6.2f}°  "
               f"(สัมบูรณ์ {n_['longitude']:8.3f}°)  เจ้าเรือน {n_['ดาวเจ้าเรือน(ลัคนาธิปติ)']}")
    out.append("  >> ลัคนาตกคนละราศี" if c["ลัคนา"]["ต่างราศี"] else "  >> ลัคนาตกราศีเดียวกัน")
    out.append("")
    out.append("  ความไวต่อเวลาเกิด (ระยะจากลัคนาถึงเส้นแบ่งราศี)")
    for label, ch in (("สายนะ  ", s_), ("นิรายนะ", n_)):
        bd = ch["ระยะถึงเส้นแบ่งราศี"]
        flag = "   <-- ใกล้เส้นแบ่ง ระวังเวลาเกิดคลาด" if min(
            bd["องศาถึงเส้นแบ่งราศีถัดไป"], bd["องศาจากเส้นแบ่งราศีก่อนหน้า"]) < 2 else ""
        out.append(f"    {label} : เข้าราศีมาแล้ว {bd['องศาจากเส้นแบ่งราศีก่อนหน้า']:6.2f}° "
                   f"({bd['นาทีจากเส้นแบ่งก่อนหน้า']:5.1f} นาที) | "
                   f"อีก {bd['องศาถึงเส้นแบ่งราศีถัดไป']:6.2f}° "
                   f"({bd['นาทีของเวลาเกิด']:5.1f} นาที) จะข้ามราศี{flag}")

    out.append("")
    out.append("── ฤกษ์ของลัคนา ──")
    for label, ch in (("สายนะ  ", s_), ("นิรายนะ", n_)):
        r = ch["ฤกษ์"]
        out.append(f"  {label} : นักษัตรที่ {r['นักษัตรที่']} {r['นักษัตร']} = {r['ฤกษ์']}ฤกษ์ "
                   f"บาท {r['บาท']} เดินไป {r['เดินไปแล้ว_%']}%")
        out.append(f"            เหลืออีก {r['เหลืออีก_องศา']}° จะเข้า {r['ฤกษ์ถัดไป']}ฤกษ์ "
                   f"({r['นักษัตรถัดไป']} เจ้าฤกษ์ {r['เจ้าฤกษ์ถัดไป']}) | เจ้าฤกษ์ปัจจุบัน {r['เจ้าฤกษ์']}")
        out.append(f"            ความหมาย {r['ฤกษ์']}: {RUEK_MEANINGS.get(r['ฤกษ์'], '—')}")

    out.append("")
    out.append("── ตรียางค์ของลัคนา ──")
    for label, ch in (("สายนะ  ", s_), ("นิรายนะ", n_)):
        t = ch["ตรียางค์"]
        out.append(f"  {label} : ตรียางค์ที่ {t['ตรียางค์ที่']} ({t['ช่วงองศา']}°) "
                   f"= ราศี{t['ราศีตรียางค์']} เจ้าตรียางค์ {t['เจ้าตรียางค์']}")

    d = c["ดิถี"]
    out.append("")
    out.append("── ดิถี (ค่าเดียวกันทั้งสองระบบ) ──")
    out.append(f"  {d['ดิถี']}  ระยะจันทร์-อาทิตย์ {d['ระยะจันทร์-อาทิตย์']}°  "
               f"ส่วนสว่าง {d['ส่วนสว่าง_%']}%")

    out.append("")
    out.append("── ตำแหน่งดาว ──")
    hdr = (f"  {_pad('ดาว', 10)}{_pad('สายนะ', 20)}{_pad('นิรายนะ', 20)}ต่าง")
    out.append(hdr)
    out.append("  " + "-" * 54)
    for p in c["ดาว"]:
        a, bb = p["สายนะ"], p["นิรายนะ"]
        ca = f"{a['ราศี']} {a['องศา']:5.2f}° {a['มาตรฐาน']}"
        cb = f"{bb['ราศี']} {bb['องศา']:5.2f}° {bb['มาตรฐาน']}"
        out.append(f"  {_pad(p['ดาว'], 10)}{_pad(ca, 20)}{_pad(cb, 20)}"
                   f"{'ต่างราศี' if p['ต่างราศี'] else ''}")

    out.append("")
    out.append("── ภพที่ดาวสถิต (นับจากลัคนาของแต่ละระบบ) ──")
    out.append(f"  {_pad('ดาว', 10)}{_pad('สายนะ', 22)}{_pad('นิรายนะ', 22)}ต่าง")
    out.append("  " + "-" * 58)
    for p in c["ดาว"]:
        a, bb = p["สายนะ"], p["นิรายนะ"]
        ca = f"ภพ {a['ภพ']} {a['ชื่อภพ']}" if a["ภพ"] else "—"
        cb = f"ภพ {bb['ภพ']} {bb['ชื่อภพ']}" if bb["ภพ"] else "—"
        out.append(f"  {_pad(p['ดาว'], 10)}{_pad(ca, 22)}{_pad(cb, 22)}"
                   f"{'ต่างภพ' if p['ต่างภพ'] else ''}")

    sm = c["สรุปความต่าง"]
    out.append("")
    out.append("── สรุป ──")
    out.append(f"  ลัคนาต่างราศี: {'ใช่' if sm['ลัคนาต่างราศี'] else 'ไม่'}   "
               f"ดาวที่ตกคนละราศี {sm['จำนวนดาวที่ต่างราศี']} ดวง   "
               f"ดาวที่ตกคนละภพ {sm['จำนวนดาวที่ต่างภพ']} ดวง")
    out.append("  ฤกษ์และตรียางค์ของลัคนาเป็นตัวชี้ขาดว่าโหรใช้ระบบไหน "
               "เพราะมันระบุองศา ไม่ใช่แค่ราศี")
    out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description="ผูกดวงโหราศาสตร์ไทย")
    p.add_argument("--date", required=True, help="วันเกิด YYYY-MM-DD (พ.ศ. หรือ ค.ศ.)")
    p.add_argument("--time", default=None,
                   help="เวลาเกิด HH:MM (24 ชม.) ถ้าไม่ระบุ ใช้ค่าเริ่มต้น 06:00 น. "
                        "(สมมุติพระอาทิตย์ขึ้น ตามธรรมเนียมสุริยยาตร์ไทยที่ verify แล้วในโปรเจกต์นี้ "
                        "ไม่ใช่ 06:55 ที่บางเครื่องมือใช้เป็น default)")
    p.add_argument("--place", help="จังหวัด (ภาษาไทยหรือ bangkok)")
    p.add_argument("--lat", type=float, help="ละติจูด (ถ้าไม่ระบุ --place)")
    p.add_argument("--lon", type=float, help="ลองจิจูด")
    p.add_argument("--ayanamsa", default="tropical", choices=["tropical", "lahiri"])
    p.add_argument("--tz", type=float, default=7.0, help="timezone offset (default 7.0 สำหรับไทย)")
    p.add_argument("--compare", action="store_true",
                   help="เทียบสายนะ (ทรอปิคัล) กับนิรายนะ (Lahiri) เคียงกัน พร้อมฤกษ์ ตรียางค์ ดิถี และค่า ayanamsa")
    p.add_argument("--format", default=None, choices=["text", "json"],
                   help="รูปแบบผลลัพธ์ (ดีฟอลต์: text เมื่อใช้ --compare, json เมื่อไม่ใช้)")
    args = p.parse_args()

    if args.place:
        key = args.place.strip().lower() if args.place.encode().isascii() else args.place.strip()
        if key not in THAI_CITIES:
            print(f"ERROR: ไม่รู้จักเมือง '{args.place}' กรุณาใส่ --lat --lon เอง", file=sys.stderr)
            print(f"เมืองที่รองรับ: {list(THAI_CITIES.keys())}", file=sys.stderr)
            sys.exit(1)
        lat, lon = THAI_CITIES[key]
    elif args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
    else:
        print("ERROR: ต้องระบุ --place หรือ --lat --lon", file=sys.stderr)
        sys.exit(1)

    fmt = args.format or ("text" if args.compare else "json")

    time_estimated = args.time is None
    time_str = args.time if args.time else "06:00"
    if time_estimated:
        print("หมายเหตุ: ไม่ได้ระบุเวลาเกิด ใช้ค่าเริ่มต้น 06:00 น. (สมมุติพระอาทิตย์ขึ้น) "
              "ลัคนา/ฤกษ์/ภพที่คำนวณได้เป็นค่าประมาณ ระบุ --time ถ้ารู้เวลาเกิดจริง", file=sys.stderr)

    if args.compare:
        result = compare_charts(args.date, time_str, lat, lon, args.tz, time_estimated)
        print(render_compare_text(result) if fmt == "text"
              else json.dumps(result, ensure_ascii=False, indent=2))
        return

    result = cast_chart(args.date, time_str, lat, lon, args.ayanamsa, args.tz, time_estimated)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
