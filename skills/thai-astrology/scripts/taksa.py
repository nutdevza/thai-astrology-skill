#!/usr/bin/env python3
"""ระบบทักษาปกรณ์ — วิเคราะห์อักษรไทยตามวันเกิด สำหรับการตั้งชื่อมงคล

Usage:
    python taksa.py --day จันทร์
    python taksa.py --day อังคาร --name "ภูมิ"
    python taksa.py --day พุธ_กลางวัน --name "ปวีณ"
"""
import argparse
import json
import sys


# พยัญชนะไทย 33 ตัว แบ่งตามวรรค (8 หมวด) ตามตำราทักษาปกรณ์
# แต่ละหมวดมีตัวอักษรที่ตกในหมวดต่างกันตาม "วันเกิด"
# โครงสร้าง: VARGAS[day][category] = [อักษร]

# วันในระบบทักษามี 8 วัน (พุธมี 2 — กลางวัน/กลางคืน)
DAY_ORDER = {
    "อาทิตย์": 0,
    "จันทร์": 1,
    "อังคาร": 2,
    "พุธ_กลางวัน": 3,
    "เสาร์": 4,
    "พฤหัสบดี": 5,
    "ราหู": 6,   # พุธ_กลางคืน
    "พุธ_กลางคืน": 6,
    "ศุกร์": 7,
}

# 8 หมวดทักษา ตามลำดับการนับ (เริ่มจากวันเกิด)
TAKSA_CATEGORIES = [
    "บริวาร",
    "อายุ",
    "เดช",
    "ศรี",
    "มูละ",
    "อุตสาหะ",
    "มนตรี",
    "กาลกิณี",
]

# พยัญชนะแบ่งเป็น 8 วรรค (ตามตำราทักษาปกรณ์มาตรฐาน)
# วรรคที่ 1: อ า อิ อี อุ อู เอ โอ (สระ-อักษรเรียง)  — แทนวันอาทิตย์
# วรรคที่ 2: ก ข ค ฆ ง — แทนวันจันทร์
# วรรคที่ 3: จ ฉ ช ฌ ญ — แทนวันอังคาร
# วรรคที่ 4: ฎ ฏ ฐ ฑ ฒ ณ — แทนวันพุธกลางวัน
# วรรคที่ 5: ด ต ถ ท ธ น — แทนวันเสาร์
# วรรคที่ 6: บ ป ผ ฝ พ ฟ ภ ม — แทนวันพฤหัสบดี
# วรรคที่ 7: ศ ษ ส ห ฬ ฮ — แทนวันราหู (พุธกลางคืน)
# วรรคที่ 8: ย ร ล ว — แทนวันศุกร์

VARGA_LETTERS = [
    ["อ", "า", "อิ", "อี", "อุ", "อู", "เอ", "โอ"],  # 0 อาทิตย์
    ["ก", "ข", "ค", "ฆ", "ง"],                          # 1 จันทร์
    ["จ", "ฉ", "ช", "ซ", "ฌ", "ญ"],                    # 2 อังคาร
    ["ฎ", "ฏ", "ฐ", "ฑ", "ฒ", "ณ"],                    # 3 พุธ กลางวัน
    ["ด", "ต", "ถ", "ท", "ธ", "น"],                    # 4 เสาร์
    ["บ", "ป", "ผ", "ฝ", "พ", "ฟ", "ภ", "ม"],         # 5 พฤหัสบดี
    ["ศ", "ษ", "ส", "ห", "ฬ", "ฮ"],                    # 6 ราหู (พุธกลางคืน)
    ["ย", "ร", "ล", "ว"],                              # 7 ศุกร์
]


def build_taksa_for_day(day: str):
    """คืน mapping {หมวด: [อักษร]} สำหรับคนเกิดวันนี้

    หลักการ: เริ่มนับหมวด "บริวาร" จากวรรคที่ตรงกับวันเกิด
    แล้วนับเวียนไป 8 หมวด
    """
    if day not in DAY_ORDER:
        raise ValueError(f"วันไม่ถูกต้อง: {day} (ต้องเป็น {list(DAY_ORDER.keys())})")
    start_idx = DAY_ORDER[day]
    result = {}
    for i, category in enumerate(TAKSA_CATEGORIES):
        varga_idx = (start_idx + i) % 8
        result[category] = {
            "วรรค": varga_idx + 1,
            "อักษร": VARGA_LETTERS[varga_idx]
        }
    return result


def find_letter_category(letter: str, taksa_map: dict):
    """หาว่าอักษรอยู่ในหมวดใด"""
    for category, info in taksa_map.items():
        if letter in info["อักษร"]:
            return category
    return None


def analyze_name(name: str, taksa_map: dict):
    """วิเคราะห์ชื่อ → ดูว่าอักษรแต่ละตัวอยู่หมวดใด"""
    analysis = []
    for ch in name:
        # ข้ามสระ/วรรณยุกต์ที่ไม่ใช่พยัญชนะหลัก (ยกเว้นวรรคที่ 1 ที่นับสระด้วย)
        cat = find_letter_category(ch, taksa_map)
        if cat:
            analysis.append({"อักษร": ch, "หมวด": cat})
    return analysis


def grade_name(analysis: list):
    """ให้คะแนน/คำแนะนำตามผลการวิเคราะห์"""
    has_kalakini = any(a["หมวด"] == "กาลกิณี" for a in analysis)
    has_sri = any(a["หมวด"] == "ศรี" for a in analysis)
    has_dech = any(a["หมวด"] == "เดช" for a in analysis)

    notes = []
    if has_kalakini:
        notes.append("⚠️ มีอักษรในหมวด 'กาลกิณี' — ควรเลี่ยง")
    if has_sri:
        notes.append("✨ มีอักษรในหมวด 'ศรี' — เสริมโชคลาภเสน่ห์")
    if has_dech:
        notes.append("✨ มีอักษรในหมวด 'เดช' — เสริมอำนาจบารมี")

    if has_kalakini:
        verdict = "ไม่แนะนำ"
    elif has_sri and has_dech:
        verdict = "ดีมาก"
    elif has_sri or has_dech:
        verdict = "ดี"
    else:
        verdict = "พอใช้"

    return {"คำแนะนำ": notes, "ผลรวม": verdict}


def main():
    p = argparse.ArgumentParser(description="วิเคราะห์ทักษาตามวันเกิด")
    p.add_argument("--day", required=True,
                   help=f"วันเกิด ({list(DAY_ORDER.keys())})")
    p.add_argument("--name", help="ชื่อที่ต้องการวิเคราะห์ (ภาษาไทย)")
    args = p.parse_args()

    try:
        taksa_map = build_taksa_for_day(args.day)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output = {"วันเกิด": args.day, "ทักษา": taksa_map}

    if args.name:
        analysis = analyze_name(args.name, taksa_map)
        grading = grade_name(analysis)
        output["ชื่อที่วิเคราะห์"] = args.name
        output["การวิเคราะห์"] = analysis
        output["ผลการประเมิน"] = grading

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
