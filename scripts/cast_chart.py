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
               ayanamsa: str = "tropical", tz_offset: float = 7.0):
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

    return {
        "ข้อมูลเกิด": {
            "วันเกิด_คศ": f"{year}-{month:02d}-{day:02d}",
            "เวลาเกิด": time_str,
            "ละติจูด": lat,
            "ลองจิจูด": lon,
            "ระบบ": "Sayana (Tropical)" if ayanamsa == "tropical" else "Nirayana (Lahiri)"
        },
        "ลัคนา": {
            "ราศี": lakkana_rasi,
            "องศา": round(lakkana_deg, 2),
            "ดาวเจ้าเรือน(ลัคนาธิปติ)": lakkana_lord
        },
        "ดาว": planets_out,
        "ภพ": bhava_map
    }


def main():
    p = argparse.ArgumentParser(description="ผูกดวงโหราศาสตร์ไทย")
    p.add_argument("--date", required=True, help="วันเกิด YYYY-MM-DD (พ.ศ. หรือ ค.ศ.)")
    p.add_argument("--time", required=True, help="เวลาเกิด HH:MM (24 ชม.)")
    p.add_argument("--place", help="จังหวัด (ภาษาไทยหรือ bangkok)")
    p.add_argument("--lat", type=float, help="ละติจูด (ถ้าไม่ระบุ --place)")
    p.add_argument("--lon", type=float, help="ลองจิจูด")
    p.add_argument("--ayanamsa", default="tropical", choices=["tropical", "lahiri"])
    p.add_argument("--tz", type=float, default=7.0, help="timezone offset (default 7.0 สำหรับไทย)")
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

    result = cast_chart(args.date, args.time, lat, lon, args.ayanamsa, args.tz)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
