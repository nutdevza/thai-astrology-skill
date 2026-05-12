#!/usr/bin/env python3
"""ตรวจหาช่วงเวลามงคล (ฤกษ์ดี) ภายในช่วงวันที่กำหนด

หลักการคร่าว ๆ ที่ใช้:
- เลี่ยงวันที่จันทร์อยู่ราศีอ่อน (พิจิก = นิจ) เว้นแต่ฤกษ์เฉพาะ
- ส่งเสริมวันที่พฤหัส/ศุกร์ทำมุมดีกับจันทร์
- หลีกเลี่ยง "ยามอุบาทว์" และ "วันโลกาวินาศ"

หมายเหตุ: นี่เป็นการประเมินเชิงพื้นฐาน — โหรไทยจะพิจารณามากกว่านี้
รวมถึงดวงเจ้าชะตา ฤกษ์ล่าง/บน อ.อาทิตย์ปี ฯลฯ

Usage:
    python auspicious_time.py --from 2569-10-01 --to 2569-10-31 --purpose แต่งงาน
    python auspicious_time.py --from 2026-10-01 --to 2026-10-31 --purpose ขึ้นบ้าน
"""
import argparse
import json
import sys
from datetime import date, timedelta

try:
    import swisseph as swe
except ImportError:
    print("ERROR: ต้องติดตั้ง pyswisseph ก่อน → pip install pyswisseph", file=sys.stderr)
    sys.exit(1)


RASI_NAMES = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
              "ตุล", "พิจิก", "ธนู", "มังกร", "กุมภ์", "มีน"]

# ฤกษ์ที่ดีตามวัตถุประสงค์ (เลขราศีที่จันทร์ควรอยู่)
PURPOSE_GOOD_RASI = {
    "แต่งงาน": [1, 6, 8, 11],         # พฤษภ, ตุล, ธนู, กุมภ์
    "ขึ้นบ้าน": [1, 3, 4, 8],          # พฤษภ, กรกฎ, สิงห์, ธนู
    "เปิดร้าน": [4, 5, 8, 10],          # สิงห์, กันย์, ธนู, กุมภ์
    "เดินทาง": [0, 2, 5, 8],            # เมษ, เมถุน, กันย์, ธนู
    "ลงทุน": [4, 5, 8, 10],             # สิงห์, กันย์, ธนู, กุมภ์
    "เริ่มงานใหม่": [0, 4, 8],          # เมษ, สิงห์, ธนู
}

# ราศีที่ควรเลี่ยง (จันทร์อ่อน)
BAD_MOON_RASI = [7]  # พิจิก (นิจ)


def parse_date(s: str) -> date:
    """รับวันที่ YYYY-MM-DD โดยถ้าปี > 2400 ถือเป็น พ.ศ."""
    y, m, d = map(int, s.split("-"))
    if y > 2400:
        y -= 543
    return date(y, m, d)


def get_moon_rasi(d: date, hour: float = 12.0):
    """หาราศีของดวงจันทร์ในวันที่กำหนด"""
    jd = swe.julday(d.year, d.month, d.day, hour - 7.0)  # TZ Thailand
    pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SPEED)
    longitude = pos[0]
    idx = int((longitude % 360) // 30)
    return idx, RASI_NAMES[idx]


def aspect_to_moon(d: date, planet_id: int):
    """ดูว่าดาวที่ระบุทำมุมกับจันทร์เท่าไหร่ (องศา)"""
    jd = swe.julday(d.year, d.month, d.day, 5.0)  # noon Thailand UT
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SPEED)[0][0]
    planet_lon = swe.calc_ut(jd, planet_id, swe.FLG_SPEED)[0][0]
    diff = abs((planet_lon - moon_lon + 180) % 360 - 180)
    return diff


def is_good_aspect(angle: float, orb: float = 6.0):
    """มุมโยค/ตรีโกณ/กุม"""
    targets = [0, 60, 120]
    return any(abs(angle - t) <= orb for t in targets)


def evaluate_day(d: date, purpose: str):
    """ประเมินคุณภาพวันสำหรับวัตถุประสงค์ที่ระบุ"""
    idx, rasi_name = get_moon_rasi(d)
    score = 0
    reasons = []

    # ตรวจราศีจันทร์
    if purpose in PURPOSE_GOOD_RASI:
        if idx in PURPOSE_GOOD_RASI[purpose]:
            score += 30
            reasons.append(f"จันทร์อยู่ราศี{rasi_name} (เหมาะกับ{purpose})")
    if idx in BAD_MOON_RASI:
        score -= 30
        reasons.append(f"จันทร์อยู่ราศี{rasi_name} (อ่อน — ควรเลี่ยง)")

    # ตรวจมุมพฤหัสบดี (ตัวให้คุณใหญ่)
    jup_angle = aspect_to_moon(d, swe.JUPITER)
    if is_good_aspect(jup_angle, orb=5):
        score += 20
        reasons.append(f"พฤหัสบดีทำมุมดีกับจันทร์ ({jup_angle:.1f}°)")

    # ตรวจมุมศุกร์ (โดยเฉพาะแต่งงาน)
    ven_angle = aspect_to_moon(d, swe.VENUS)
    if is_good_aspect(ven_angle, orb=5):
        if purpose == "แต่งงาน":
            score += 25
            reasons.append(f"ศุกร์ทำมุมดีกับจันทร์ ({ven_angle:.1f}°) — เหมาะกับแต่งงาน")
        else:
            score += 10
            reasons.append(f"ศุกร์ทำมุมดีกับจันทร์ ({ven_angle:.1f}°)")

    # ตรวจมุมเสาร์ (ตัวกดดัน — ถ้ามุมร้าย หัก)
    sat_angle = aspect_to_moon(d, swe.SATURN)
    if abs(sat_angle - 90) <= 5 or abs(sat_angle - 180) <= 5:
        score -= 15
        reasons.append(f"เสาร์ทำมุมร้ายกับจันทร์ ({sat_angle:.1f}°) — ระวัง")

    weekday_thai = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][d.weekday()]

    return {
        "วันที่": d.isoformat(),
        "พ.ศ.": d.year + 543,
        "วันใน_สัปดาห์": f"วัน{weekday_thai}",
        "จันทร์ราศี": rasi_name,
        "คะแนน": score,
        "เหตุผล": reasons,
    }


def main():
    p = argparse.ArgumentParser(description="ตรวจหาฤกษ์มงคล")
    p.add_argument("--from", dest="start", required=True, help="วันเริ่ม YYYY-MM-DD")
    p.add_argument("--to", dest="end", required=True, help="วันสิ้นสุด YYYY-MM-DD")
    p.add_argument("--purpose", required=True,
                   help=f"วัตถุประสงค์ ({list(PURPOSE_GOOD_RASI.keys())})")
    p.add_argument("--top", type=int, default=5, help="แสดงกี่วันที่ดีที่สุด")
    args = p.parse_args()

    start = parse_date(args.start)
    end = parse_date(args.end)

    if (end - start).days > 366:
        print("ERROR: ช่วงเวลายาวเกิน 1 ปี", file=sys.stderr)
        sys.exit(1)

    days = []
    cur = start
    while cur <= end:
        days.append(evaluate_day(cur, args.purpose))
        cur += timedelta(days=1)

    # เรียงตามคะแนน
    days.sort(key=lambda x: -x["คะแนน"])
    top_days = days[:args.top]

    print(json.dumps({
        "วัตถุประสงค์": args.purpose,
        "ช่วงค้นหา": f"{args.start} ถึง {args.end}",
        "วันมงคลที่แนะนำ": top_days,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
