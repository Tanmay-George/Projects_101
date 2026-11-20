"""Continuity – Digital Prop Closet & Scene Tracker.
Flask REST API backed by MySQL 8.  Run `mysql -u root -p < database/schema.sql`
and `mysql -u root -p < database/seed.sql` before selecting APP_MODE=mysql.
"""
from __future__ import annotations

import copy
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()
ROOT = Path(__file__).parent
app = Flask(__name__, static_folder="static", static_url_path="")
app.config["JSON_SORT_KEYS"] = False

APP_MODE = os.getenv("APP_MODE", "auto").lower()
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "continuity_tracker"),
    "connection_timeout": int(os.getenv("MYSQL_CONNECT_TIMEOUT", "3")),
}


def json_default(value: Any):
    if isinstance(value, (datetime, )):
        return value.isoformat(sep=" ", timespec="minutes")
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


# A limited local preview data layer allows the UI to be inspected before MySQL is configured.
# It is never used when APP_MODE=mysql.
DEMO: dict[str, list[dict[str, Any]]] = {'productions': [{'ProductionID': 1,
                  'Title': 'Baahubali 2 — Final Battle Continuity Study',
                  'Director': 'S. S. Rajamouli',
                  'StartDate': '2017-04-28',
                  'EndDate': '2017-04-28',
                  'Status': 'In production',
                  'ProductionBudget': 2500000000,
                  'Notes': 'Academic continuity breakdown of the final Mahishmati confrontation. Scene labels and '
                           'production notes are created for this tracker, not official screenplay material.'}],
 'scenes': [{'SceneID': 1,
             'ProductionID': 1,
             'SceneNumber': 'F01',
             'Description': 'Mahendra Baahubali reaches the royal courtyard as the final confrontation begins.',
             'Setting': 'Mahishmati palace courtyard',
             'TimeOfDay': 'Day',
             'Pages': 2.0,
             'ScriptPageStart': 1,
             'ScriptPageEnd': 3},
            {'SceneID': 2,
             'ProductionID': 1,
             'SceneNumber': 'F02',
             'Description': 'Bhallaladeva’s royal guard closes the courtyard while Devasena remains within the '
                            'palace precinct.',
             'Setting': 'Mahishmati palace courtyard — eastern gate',
             'TimeOfDay': 'Day',
             'Pages': 2.5,
             'ScriptPageStart': 3,
             'ScriptPageEnd': 5.5},
            {'SceneID': 3,
             'ProductionID': 1,
             'SceneNumber': 'F03',
             'Description': 'The defenders regroup among the stone pavilions and the royal banners are reset after '
                            'the first clash.',
             'Setting': 'Mahishmati stone pavilion',
             'TimeOfDay': 'Day',
             'Pages': 1.75,
             'ScriptPageStart': 5.5,
             'ScriptPageEnd': 7.25},
            {'SceneID': 4,
             'ProductionID': 1,
             'SceneNumber': 'F04',
             'Description': 'Mahendra and Bhallaladeva enter the central arena for the close-quarters duel.',
             'Setting': 'Mahishmati royal arena',
             'TimeOfDay': 'Day',
             'Pages': 3.0,
             'ScriptPageStart': 7.25,
             'ScriptPageEnd': 10.25},
            {'SceneID': 5,
             'ProductionID': 1,
             'SceneNumber': 'F05',
             'Description': 'The duel moves through the damaged throne approach; weapon condition and hand position '
                            'must match across coverage.',
             'Setting': 'Throne approach and forge platform',
             'TimeOfDay': 'Day',
             'Pages': 2.25,
             'ScriptPageStart': 10.25,
             'ScriptPageEnd': 12.5},
            {'SceneID': 6,
             'ProductionID': 1,
             'SceneNumber': 'F06',
             'Description': 'Bhallaladeva is defeated; the courtyard clears for Devasena’s final act of justice.',
             'Setting': 'Mahishmati execution courtyard',
             'TimeOfDay': 'Dusk',
             'Pages': 2.0,
             'ScriptPageStart': 12.5,
             'ScriptPageEnd': 14.5},
            {'SceneID': 7,
             'ProductionID': 1,
             'SceneNumber': 'F07',
             'Description': 'Aftermath in Mahishmati: the royal standard returns and the new order is witnessed by '
                            'the court.',
             'Setting': 'Mahishmati throne courtyard',
             'TimeOfDay': 'Dusk',
             'Pages': 1.5,
             'ScriptPageStart': 14.5,
             'ScriptPageEnd': 16}],
 'characters': [{'CharacterID': 1,
                 'Name': 'Mahendra Baahubali',
                 'ActorName': 'Prabhas',
                 'Notes': 'Hero weapon continuity: bow grip, right-hand battle sword, and dust level on armour.'},
                {'CharacterID': 2,
                 'Name': 'Bhallaladeva',
                 'ActorName': 'Rana Daggubati',
                 'Notes': 'Primary opponent. Track mace orientation, armour damage, and arena-side entrances.'},
                {'CharacterID': 3,
                 'Name': 'Devasena',
                 'ActorName': 'Anushka Shetty',
                 'Notes': 'Track bow hand-off, veil / costume condition, and position at the execution courtyard.'},
                {'CharacterID': 4,
                 'Name': 'Kattappa',
                 'ActorName': 'Sathyaraj',
                 'Notes': 'Royal guard weapon and shoulder armour remain consistent during courtyard coverage.'},
                {'CharacterID': 5,
                 'Name': 'Bijjaladeva',
                 'ActorName': 'Nassar',
                 'Notes': 'Court witness context for aftermath and throne-courtyard reaction coverage.'}],
 'props': [{'PropID': 1,
            'Name': 'Baahubali hero bow',
            'Description': 'Carved dark-wood hero bow used for Mahendra’s courtyard coverage.',
            'Category': 'Hero prop',
            'BaseCondition': 'Battle-worn',
            'CurrentLocation': 'Hero rack · Arena unit',
            'CurrentStatus': 'In Use',
            'LastInventoriedDate': '2017-04-28 07:10'},
           {'PropID': 2,
            'Name': 'Bhallaladeva war mace',
            'Description': 'Large iron-finish mace with controlled battle scuffs for the central duel.',
            'Category': 'Hero prop',
            'BaseCondition': 'Battle-worn',
            'CurrentLocation': 'Bhallaladeva stand-in case',
            'CurrentStatus': 'In Use',
            'LastInventoriedDate': '2017-04-28 07:12'},
           {'PropID': 3,
            'Name': 'Mahendra battle sword',
            'Description': 'Hero sword with dulled camera-safe edge and marked right-hand grip.',
            'Category': 'Hero prop',
            'BaseCondition': 'Battle-worn',
            'CurrentLocation': 'Hero rack · Arena unit',
            'CurrentStatus': 'Available',
            'LastInventoriedDate': '2017-04-28 07:08'},
           {'PropID': 4,
            'Name': 'Devasena bow',
            'Description': 'Ceremonial bow used in palace precinct and execution-courtyard coverage.',
            'Category': 'Hero prop',
            'BaseCondition': 'Aged',
            'CurrentLocation': 'Devasena prop station',
            'CurrentStatus': 'Available',
            'LastInventoriedDate': '2017-04-28 07:04'},
           {'PropID': 5,
            'Name': 'Royal standard — Mahishmati',
            'Description': 'Gold-edged royal banner; tear pattern must remain camera-left after F03.',
            'Category': 'Set dressing',
            'BaseCondition': 'Damaged',
            'CurrentLocation': 'Stone pavilion reset cart',
            'CurrentStatus': 'Available',
            'LastInventoriedDate': '2017-04-28 06:55'},
           {'PropID': 6,
            'Name': 'Forged iron chain',
            'Description': 'Arena chain section used for the throne-approach and forge-platform action.',
            'Category': 'Hand prop',
            'BaseCondition': 'Battle-worn',
            'CurrentLocation': 'Forge platform · marked position',
            'CurrentStatus': 'In Use',
            'LastInventoriedDate': '2017-04-28 07:15'},
           {'PropID': 7,
            'Name': 'Royal guard shield',
            'Description': 'Embossed bronze shield for Kattappa and royal guard foreground action.',
            'Category': 'Hand prop',
            'BaseCondition': 'Damaged',
            'CurrentLocation': 'Guard cart · bay 2',
            'CurrentStatus': 'Available',
            'LastInventoriedDate': '2017-04-28 07:00'},
           {'PropID': 8,
            'Name': 'Arena fire brazier',
            'Description': 'Controlled flame brazier for the execution-courtyard transition.',
            'Category': 'Set dressing',
            'BaseCondition': 'Aged',
            'CurrentLocation': 'Safety hold · courtyard west',
            'CurrentStatus': 'Broken',
            'LastInventoriedDate': '2017-04-28 06:50'},
           {'PropID': 9,
            'Name': 'Throne court seal',
            'Description': 'Brass royal seal placed on the aftermath dais.',
            'Category': 'Set dressing',
            'BaseCondition': 'Good',
            'CurrentLocation': 'Court detail case',
            'CurrentStatus': 'Available',
            'LastInventoriedDate': '2017-04-28 06:58'},
           {'PropID': 10,
            'Name': 'Bhallaladeva armour plate',
            'Description': 'Removable left shoulder armour plate with progressive battle damage.',
            'Category': 'Costume accessory',
            'BaseCondition': 'Damaged',
            'CurrentLocation': 'Costume repair tent',
            'CurrentStatus': 'Missing',
            'LastInventoriedDate': '2017-04-28 07:06'}],
 'assignments': [{'AssignmentID': 1,
                  'SceneID': 1,
                  'PropID': 1,
                  'CharacterID': 1,
                  'IsRequired': 1,
                  'UsageType': 'Holding',
                  'PlacementNotes': 'Mahendra enters with bow in left hand; lower limb faces camera right.',
                  'ActorContext': 'Mahendra establishes the confrontation.',
                  'TimeCode': '00:00:14'},
                 {'AssignmentID': 2,
                  'SceneID': 1,
                  'PropID': 5,
                  'CharacterID': None,
                  'IsRequired': 1,
                  'UsageType': 'Placed',
                  'PlacementNotes': 'Royal standard at north arcade, intact before the first clash.',
                  'ActorContext': 'Background story marker.',
                  'TimeCode': '00:00:28'},
                 {'AssignmentID': 3,
                  'SceneID': 2,
                  'PropID': 4,
                  'CharacterID': 3,
                  'IsRequired': 1,
                  'UsageType': 'Holding',
                  'PlacementNotes': 'Devasena keeps bow at her left side inside the eastern gate.',
                  'ActorContext': 'Devasena observes the guard movement.',
                  'TimeCode': '00:01:06'},
                 {'AssignmentID': 4,
                  'SceneID': 2,
                  'PropID': 7,
                  'CharacterID': 4,
                  'IsRequired': 1,
                  'UsageType': 'Holding',
                  'PlacementNotes': 'Shield face toward camera for the guard foreground reset.',
                  'ActorContext': 'Kattappa holds the defensive line.',
                  'TimeCode': '00:01:21'},
                 {'AssignmentID': 5,
                  'SceneID': 3,
                  'PropID': 5,
                  'CharacterID': None,
                  'IsRequired': 1,
                  'UsageType': 'Placed',
                  'PlacementNotes': 'Torn edge now hangs camera-left after impact coverage.',
                  'ActorContext': 'Stone pavilion continuity.',
                  'TimeCode': '00:02:02'},
                 {'AssignmentID': 6,
                  'SceneID': 4,
                  'PropID': 2,
                  'CharacterID': 2,
                  'IsRequired': 1,
                  'UsageType': 'Handling',
                  'PlacementNotes': 'Mace begins in Bhallaladeva’s right hand, head low beside his boot.',
                  'ActorContext': 'Central arena duel.',
                  'TimeCode': '00:03:10'},
                 {'AssignmentID': 7,
                  'SceneID': 4,
                  'PropID': 3,
                  'CharacterID': 1,
                  'IsRequired': 1,
                  'UsageType': 'Holding',
                  'PlacementNotes': 'Sword begins in Mahendra’s right hand; guard faces outward.',
                  'ActorContext': 'Central arena duel.',
                  'TimeCode': '00:03:12'},
                 {'AssignmentID': 8,
                  'SceneID': 5,
                  'PropID': 6,
                  'CharacterID': 1,
                  'IsRequired': 1,
                  'UsageType': 'Handling',
                  'PlacementNotes': 'Chain enters from forge platform, marked link remains visible near wrist.',
                  'ActorContext': 'Throne approach action beat.',
                  'TimeCode': '00:04:04'},
                 {'AssignmentID': 9,
                  'SceneID': 5,
                  'PropID': 10,
                  'CharacterID': 2,
                  'IsRequired': 1,
                  'UsageType': 'Worn',
                  'PlacementNotes': 'Left shoulder plate has deep scrape facing camera after the fall.',
                  'ActorContext': 'Bhallaladeva damage progression.',
                  'TimeCode': '00:04:18'},
                 {'AssignmentID': 10,
                  'SceneID': 6,
                  'PropID': 8,
                  'CharacterID': None,
                  'IsRequired': 1,
                  'UsageType': 'Placed',
                  'PlacementNotes': 'Brazier at courtyard west; flame height matches dusk plate.',
                  'ActorContext': 'Execution-courtyard atmosphere.',
                  'TimeCode': '00:05:12'},
                 {'AssignmentID': 11,
                  'SceneID': 6,
                  'PropID': 4,
                  'CharacterID': 3,
                  'IsRequired': 0,
                  'UsageType': 'Carried',
                  'PlacementNotes': 'Bow carried down at Devasena’s left side.',
                  'ActorContext': 'Devasena enters final justice beat.',
                  'TimeCode': '00:05:23'},
                 {'AssignmentID': 12,
                  'SceneID': 7,
                  'PropID': 9,
                  'CharacterID': 5,
                  'IsRequired': 1,
                  'UsageType': 'Placed',
                  'PlacementNotes': 'Seal is centered on the aftermath dais, emblem facing audience side.',
                  'ActorContext': 'Court restoration image.',
                  'TimeCode': '00:06:02'},
                 {'AssignmentID': 13,
                  'SceneID': 7,
                  'PropID': 5,
                  'CharacterID': None,
                  'IsRequired': 1,
                  'UsageType': 'Placed',
                  'PlacementNotes': 'Standard is repaired and raised at north arcade for the final image.',
                  'ActorContext': 'New-order visual cue.',
                  'TimeCode': '00:06:18'}],
 'logs': [{'LogID': 1,
           'SceneID': 4,
           'Timestamp': '2017-04-28 09:18',
           'TakeNumber': 'F04 · Take 6',
           'ContinuityIssues': 'Bhallaladeva’s mace returned to the left hand after the reverse-angle cut.',
           'ActionTaken': 'Reset mace to right hand with head low beside the boot; photographed before action.',
           'SceneNotes': 'Mahendra sword guard remains outward.'},
          {'LogID': 2,
           'SceneID': 5,
           'Timestamp': '2017-04-28 09:06',
           'TakeNumber': 'F05 · Take 3',
           'ContinuityIssues': 'Left shoulder armour plate was missing the deep scrape from the previous setup.',
           'ActionTaken': 'Sent armour plate to costume repair tent and held close coverage.',
           'SceneNotes': 'Use damage reference card B-10.'},
          {'LogID': 3,
           'SceneID': 3,
           'Timestamp': '2017-04-28 08:42',
           'TakeNumber': 'F03 · Take 4',
           'ContinuityIssues': 'Royal standard tear was reversed after pavilion reset.',
           'ActionTaken': 'Restored torn edge to camera-left and marked reset cart.',
           'SceneNotes': 'Banner must remain torn until F06 clearance.'},
          {'LogID': 4,
           'SceneID': 6,
           'Timestamp': '2017-04-28 08:21',
           'TakeNumber': 'F06 · Take 2',
           'ContinuityIssues': 'Brazier ignition was inconsistent with the dusk atmosphere plate.',
           'ActionTaken': 'Flagged brazier for safety check; prepared matching flame unit.',
           'SceneNotes': 'Devasena bow remains lowered on entry.'}]}

# These bridge rows mirror the normalized MySQL production_characters and
# production_props tables. They make the active-production scope explicit.
DEMO['production_characters'] = [
    {'ProductionID': 1, 'CharacterID': 1}, {'ProductionID': 1, 'CharacterID': 2},
    {'ProductionID': 1, 'CharacterID': 3}, {'ProductionID': 1, 'CharacterID': 4},
    {'ProductionID': 1, 'CharacterID': 5},
]
DEMO['production_props'] = [
    {'ProductionID': 1, 'PropID': prop_id, 'IsHero': prop_id in {1, 2, 3, 4, 6}}
    for prop_id in range(1, 11)
]


class MySQLStore:
    def __init__(self):
        self._available: bool | None = None
        self._error = ""

    def connect(self):
        import mysql.connector  # imported only when MySQL mode is used
        return mysql.connector.connect(**MYSQL_CONFIG)

    def available(self) -> bool:
        if APP_MODE == "demo":
            return False
        try:
            conn = self.connect()
            conn.close()
            self._available, self._error = True, ""
        except Exception as exc:
            self._available, self._error = False, str(exc)
        return bool(self._available)

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        conn = self.connect()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            rows = cur.fetchall()
            return rows
        finally:
            conn.close()

    def write(self, sql: str, params: tuple = ()) -> int:
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def batch(self, statements: list[tuple[str, tuple]]) -> None:
        """Commit multiple dependent changes as one transaction."""
        conn = self.connect()
        try:
            cur = conn.cursor()
            for sql, params in statements:
                cur.execute(sql, params)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


mysql_store = MySQLStore()


def using_mysql() -> bool:
    return mysql_store.available()


def payload() -> dict:
    return request.get_json(silent=True) or request.form.to_dict() or {}


def need(data: dict, *names: str):
    missing = [name for name in names if not str(data.get(name, "")).strip()]
    if missing:
        raise ValueError("Required: " + ", ".join(missing))


def demo_next(key: str, id_name: str) -> int:
    return max((int(x[id_name]) for x in DEMO[key]), default=0) + 1


def decorate_demo_assignments(rows: list[dict]) -> list[dict]:
    props = {p["PropID"]: p for p in DEMO["props"]}
    chars = {c["CharacterID"]: c for c in DEMO["characters"]}
    answer = []
    for row in rows:
        item = copy.deepcopy(row)
        prop = props.get(item["PropID"], {})
        character = chars.get(item.get("CharacterID"), {})
        item.update({"PropName": prop.get("Name"), "PropCategory": prop.get("Category"), "CurrentStatus": prop.get("CurrentStatus", "Available"), "CharacterName": character.get("Name")})
        answer.append(item)
    return answer


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/database/schema.sql")
def schema_sql():
    return send_from_directory(ROOT / "database", "schema.sql", mimetype="text/plain")


@app.get("/api/health")
def health():
    mysql_ok = using_mysql()
    if APP_MODE == "mysql" and not mysql_ok:
        return jsonify({"ok": False, "mode": "mysql", "message": mysql_store._error or "MySQL is unavailable"}), 503
    return jsonify({"ok": True, "mode": "mysql" if mysql_ok else "demo", "message": "MySQL 8 connected" if mysql_ok else "Demo preview — configure MySQL for persistent data"})


@app.get("/api/productions")
def productions():
    if using_mysql():
        rows = mysql_store.query("SELECT * FROM productions ORDER BY FIELD(Status,'In production','Pre-production','Post-production','Wrapped'), Title")
    else:
        rows = copy.deepcopy(DEMO["productions"])
    return jsonify(rows)


@app.post("/api/productions")
def create_production():
    data = payload()
    try:
        need(data, "Title")
        if using_mysql():
            new_id = mysql_store.write("""INSERT INTO productions (Title,Director,StartDate,EndDate,Status,ProductionBudget,Notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""", (data["Title"], data.get("Director"), data.get("StartDate") or None, data.get("EndDate") or None, data.get("Status", "Pre-production"), data.get("ProductionBudget") or 0, data.get("Notes")))
            item = mysql_store.query("SELECT * FROM productions WHERE ProductionID=%s", (new_id,))[0]
        else:
            item = {"ProductionID": demo_next("productions", "ProductionID"), "Title": data["Title"], "Director": data.get("Director"), "Status": data.get("Status", "Pre-production"), "ProductionBudget": float(data.get("ProductionBudget") or 0), "StartDate": data.get("StartDate"), "EndDate": data.get("EndDate"), "Notes": data.get("Notes")}
            DEMO["productions"].append(item)
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/productions/<int:production_id>")
def update_production(production_id):
    data = payload()
    try:
        need(data, "Title")
        if using_mysql():
            mysql_store.write("""UPDATE productions SET Title=%s, Director=%s, StartDate=%s, EndDate=%s,
                Status=%s, ProductionBudget=%s, Notes=%s WHERE ProductionID=%s""", (data["Title"], data.get("Director"), data.get("StartDate") or None, data.get("EndDate") or None, data.get("Status", "Pre-production"), data.get("ProductionBudget") or 0, data.get("Notes"), production_id))
            item = mysql_store.query("SELECT * FROM productions WHERE ProductionID=%s", (production_id,))
            if not item: return jsonify({"error": "Production not found"}), 404
            return jsonify(item[0])
        item = next((p for p in DEMO["productions"] if p["ProductionID"] == production_id), None)
        if not item: return jsonify({"error": "Production not found"}), 404
        item.update({k: data.get(k) for k in ("Title", "Director", "StartDate", "EndDate", "Status", "ProductionBudget", "Notes")})
        item["ProductionBudget"] = float(item["ProductionBudget"] or 0)
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/productions/<int:production_id>")
def delete_production(production_id):
    if using_mysql():
        mysql_store.write("DELETE FROM productions WHERE ProductionID=%s", (production_id,))
    else:
        if not any(p["ProductionID"] == production_id for p in DEMO["productions"]): return jsonify({"error": "Production not found"}), 404
        scene_ids = {s["SceneID"] for s in DEMO["scenes"] if s["ProductionID"] == production_id}
        DEMO["productions"][:] = [p for p in DEMO["productions"] if p["ProductionID"] != production_id]
        DEMO["scenes"][:] = [s for s in DEMO["scenes"] if s["ProductionID"] != production_id]
        DEMO["production_characters"][:] = [r for r in DEMO["production_characters"] if r["ProductionID"] != production_id]
        DEMO["production_props"][:] = [r for r in DEMO["production_props"] if r["ProductionID"] != production_id]
        DEMO["assignments"][:] = [a for a in DEMO["assignments"] if a["SceneID"] not in scene_ids]
        DEMO["logs"][:] = [l for l in DEMO["logs"] if l["SceneID"] not in scene_ids]
    return "", 204


@app.get("/api/scenes")
def scenes():
    production_id = request.args.get("production_id", type=int)
    if using_mysql():
        sql = """SELECT s.*, COUNT(a.AssignmentID) AS AssignmentCount,
                 COALESCE(SUM(a.IsRequired=1),0) AS RequiredCount,
                 COALESCE(SUM(cur.CurrentStatus IN ('Missing','Broken')),0) AS AtRiskCount
                 FROM scenes s LEFT JOIN unified_prop_assignments a ON a.SceneID=s.SceneID
                 LEFT JOIN vw_prop_current_status cur ON cur.PropID=a.PropID"""
        params: tuple = ()
        if production_id:
            sql += " WHERE s.ProductionID=%s"; params = (production_id,)
        sql += " GROUP BY s.SceneID ORDER BY CAST(REGEXP_REPLACE(s.SceneNumber,'[^0-9.]','') AS DECIMAL(10,2)), s.SceneNumber"
        rows = mysql_store.query(sql, params)
    else:
        rows = [copy.deepcopy(x) for x in DEMO["scenes"] if not production_id or x["ProductionID"] == production_id]
        for s in rows:
            ass = [a for a in DEMO["assignments"] if a["SceneID"] == s["SceneID"]]
            at_risk = [a for a in ass if next((p for p in DEMO["props"] if p["PropID"] == a["PropID"]), {}).get("CurrentStatus") in ("Missing", "Broken")]
            s.update({"AssignmentCount": len(ass), "RequiredCount": sum(a["IsRequired"] for a in ass), "AtRiskCount": len(at_risk)})
    return jsonify(rows)


@app.post("/api/scenes")
def create_scene():
    data = payload()
    try:
        need(data, "ProductionID", "SceneNumber", "Setting")
        if using_mysql():
            new_id = mysql_store.write("""INSERT INTO scenes (ProductionID,SceneNumber,Description,Setting,TimeOfDay,Pages,ScriptPageStart,ScriptPageEnd)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (data["ProductionID"], data["SceneNumber"], data.get("Description"), data["Setting"], data.get("TimeOfDay", "Unknown"), data.get("Pages") or None, data.get("ScriptPageStart") or None, data.get("ScriptPageEnd") or None))
            item = mysql_store.query("SELECT * FROM scenes WHERE SceneID=%s", (new_id,))[0]
        else:
            item = {"SceneID": demo_next("scenes", "SceneID"), **data, "AssignmentCount": 0, "RequiredCount": 0, "AtRiskCount": 0}
            item["ProductionID"] = int(item["ProductionID"]); DEMO["scenes"].append(item)
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/scenes/<int:scene_id>")
def update_scene(scene_id):
    data = payload()
    try:
        need(data, "ProductionID", "SceneNumber", "Setting")
        if using_mysql():
            mysql_store.write("""UPDATE scenes SET ProductionID=%s, SceneNumber=%s, Description=%s, Setting=%s,
                 TimeOfDay=%s, Pages=%s, ScriptPageStart=%s, ScriptPageEnd=%s WHERE SceneID=%s""", (data["ProductionID"], data["SceneNumber"], data.get("Description"), data["Setting"], data.get("TimeOfDay", "Unknown"), data.get("Pages") or None, data.get("ScriptPageStart") or None, data.get("ScriptPageEnd") or None, scene_id))
            item = mysql_store.query("SELECT * FROM scenes WHERE SceneID=%s", (scene_id,))
            if not item: return jsonify({"error": "Scene not found"}), 404
            return jsonify(item[0])
        item = next((s for s in DEMO["scenes"] if s["SceneID"] == scene_id), None)
        if not item: return jsonify({"error": "Scene not found"}), 404
        item.update(data); item["ProductionID"] = int(item["ProductionID"])
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/scenes/<int:scene_id>")
def delete_scene(scene_id):
    if using_mysql():
        mysql_store.write("DELETE FROM scenes WHERE SceneID=%s", (scene_id,))
    else:
        if not any(s["SceneID"] == scene_id for s in DEMO["scenes"]): return jsonify({"error": "Scene not found"}), 404
        DEMO["scenes"][:] = [s for s in DEMO["scenes"] if s["SceneID"] != scene_id]
        DEMO["assignments"][:] = [a for a in DEMO["assignments"] if a["SceneID"] != scene_id]
        DEMO["logs"][:] = [l for l in DEMO["logs"] if l["SceneID"] != scene_id]
    return "", 204


@app.get("/api/characters")
def characters():
    production_id = request.args.get("production_id", type=int)
    if using_mysql():
        if production_id:
            rows = mysql_store.query("""SELECT c.*, pc.ProductionID, pc.BillingOrder, pc.ProductionNotes
                FROM characters c JOIN production_characters pc ON pc.CharacterID=c.CharacterID
                WHERE pc.ProductionID=%s ORDER BY pc.BillingOrder IS NULL, pc.BillingOrder, c.Name""", (production_id,))
        else:
            rows = mysql_store.query("SELECT * FROM characters ORDER BY Name")
    else:
        rows = copy.deepcopy(DEMO["characters"])
        if production_id:
            character_ids = {r["CharacterID"] for r in DEMO["production_characters"] if r["ProductionID"] == production_id}
            rows = [dict(c, ProductionID=production_id) for c in rows if c["CharacterID"] in character_ids]
    return jsonify(rows)


@app.post("/api/characters")
def create_character():
    data = payload()
    try:
        need(data, "Name")
        production_id = int(data["ProductionID"]) if data.get("ProductionID") else None
        if using_mysql():
            new_id = mysql_store.write("INSERT INTO characters (Name,ActorName,Notes) VALUES (%s,%s,%s)", (data["Name"], data.get("ActorName"), data.get("Notes")))
            if production_id:
                mysql_store.write("INSERT INTO production_characters (ProductionID,CharacterID) VALUES (%s,%s)", (production_id, new_id))
            item = mysql_store.query("SELECT * FROM characters WHERE CharacterID=%s", (new_id,))[0]
            item["ProductionID"] = production_id
        else:
            item = {"CharacterID": demo_next("characters", "CharacterID"), "Name": data["Name"], "ActorName": data.get("ActorName"), "Notes": data.get("Notes"), "ProductionID": production_id}
            DEMO["characters"].append(item)
            if production_id: DEMO["production_characters"].append({"ProductionID": production_id, "CharacterID": item["CharacterID"]})
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/characters/<int:character_id>")
def update_character(character_id):
    data = payload()
    try:
        need(data, "Name")
        production_id = int(data["ProductionID"]) if data.get("ProductionID") else None
        if using_mysql():
            mysql_store.write("UPDATE characters SET Name=%s, ActorName=%s, Notes=%s WHERE CharacterID=%s", (data["Name"], data.get("ActorName"), data.get("Notes"), character_id))
            if production_id:
                mysql_store.write("INSERT INTO production_characters (ProductionID,CharacterID) VALUES (%s,%s) ON DUPLICATE KEY UPDATE ProductionID=VALUES(ProductionID)", (production_id, character_id))
            item = mysql_store.query("SELECT * FROM characters WHERE CharacterID=%s", (character_id,))
            if not item: return jsonify({"error": "Character not found"}), 404
            item[0]["ProductionID"] = production_id
            return jsonify(item[0])
        item = next((c for c in DEMO["characters"] if c["CharacterID"] == character_id), None)
        if not item: return jsonify({"error": "Character not found"}), 404
        item.update({"Name":data["Name"], "ActorName":data.get("ActorName"), "Notes":data.get("Notes"), "ProductionID":production_id or item.get("ProductionID")})
        if production_id and not any(r["ProductionID"] == production_id and r["CharacterID"] == character_id for r in DEMO["production_characters"]):
            DEMO["production_characters"].append({"ProductionID":production_id,"CharacterID":character_id})
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/characters/<int:character_id>")
def delete_character(character_id):
    if using_mysql():
        mysql_store.write("DELETE FROM characters WHERE CharacterID=%s", (character_id,))
    else:
        if not any(c["CharacterID"] == character_id for c in DEMO["characters"]): return jsonify({"error": "Character not found"}), 404
        DEMO["characters"][:] = [c for c in DEMO["characters"] if c["CharacterID"] != character_id]
        DEMO["production_characters"][:] = [r for r in DEMO["production_characters"] if r["CharacterID"] != character_id]
        for assignment in DEMO["assignments"]:
            if assignment.get("CharacterID") == character_id: assignment["CharacterID"] = None
    return "", 204


@app.get("/api/props")
def props():
    production_id = request.args.get("production_id", type=int)
    status = request.args.get("status")
    search = request.args.get("search", "").strip()
    if using_mysql():
        if production_id:
            sql = """SELECT cur.*, pp.ProductionID FROM vw_prop_current_status cur
                JOIN production_props pp ON pp.PropID=cur.PropID WHERE pp.ProductionID=%s"""; params: list = [production_id]
        else:
            sql = "SELECT * FROM vw_prop_current_status WHERE 1=1"; params = []
        if status and status != "All": sql += " AND CurrentStatus=%s"; params.append(status)
        if search: sql += " AND (Name LIKE %s OR Category LIKE %s)"; params += [f"%{search}%", f"%{search}%"]
        sql += " ORDER BY FIELD(CurrentStatus,'Missing','Broken','In Use','Available'), Name"
        rows = mysql_store.query(sql, tuple(params))
    else:
        rows = copy.deepcopy(DEMO["props"])
        if production_id:
            prop_ids = {r["PropID"] for r in DEMO["production_props"] if r["ProductionID"] == production_id}
            rows = [dict(p, ProductionID=production_id) for p in rows if p["PropID"] in prop_ids]
        if status and status != "All": rows = [p for p in rows if p["CurrentStatus"] == status]
        if search: rows = [p for p in rows if search.lower() in (p["Name"] + p["Category"]).lower()]
    return jsonify(rows)


@app.post("/api/props")
def create_prop():
    data = payload()
    try:
        need(data, "Name", "Category")
        production_id = int(data["ProductionID"]) if data.get("ProductionID") else None
        if using_mysql():
            new_id = mysql_store.write("INSERT INTO props (Name,Description,Category,BaseCondition) VALUES (%s,%s,%s,%s)", (data["Name"], data.get("Description"), data["Category"], data.get("BaseCondition", "Good")))
            mysql_store.write("INSERT INTO prop_inventory_status (PropID,CurrentLocation,CurrentStatus,AcquisitionCost,Notes) VALUES (%s,%s,%s,%s,%s)", (new_id, data.get("CurrentLocation", "Unassigned"), data.get("CurrentStatus", "Available"), data.get("AcquisitionCost") or 0, data.get("InventoryNotes")))
            if production_id:
                mysql_store.write("INSERT INTO production_props (ProductionID,PropID,IsHero) VALUES (%s,%s,%s)", (production_id, new_id, data.get("Category") == "Hero prop"))
            item = mysql_store.query("SELECT * FROM vw_prop_current_status WHERE PropID=%s", (new_id,))[0]
            item["ProductionID"] = production_id
        else:
            item = {"PropID": demo_next("props", "PropID"), "Name": data["Name"], "Description": data.get("Description"), "Category": data["Category"], "BaseCondition": data.get("BaseCondition", "Good"), "CurrentLocation": data.get("CurrentLocation", "Unassigned"), "CurrentStatus": data.get("CurrentStatus", "Available"), "LastInventoriedDate": datetime.now().strftime("%Y-%m-%d %H:%M"), "ProductionID": production_id}
            DEMO["props"].append(item)
            if production_id: DEMO["production_props"].append({"ProductionID":production_id,"PropID":item["PropID"],"IsHero":data.get("Category") == "Hero prop"})
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/props/<int:prop_id>")
def update_prop(prop_id):
    data = payload()
    try:
        need(data, "Name", "Category")
        production_id = int(data["ProductionID"]) if data.get("ProductionID") else None
        if using_mysql():
            statements = [("UPDATE props SET Name=%s, Description=%s, Category=%s, BaseCondition=%s WHERE PropID=%s", (data["Name"], data.get("Description"), data["Category"], data.get("BaseCondition", "Good"), prop_id))]
            # Status/location edits are recorded as a new auditable inventory snapshot.
            if data.get("CurrentStatus"):
                statements.append(("INSERT INTO prop_inventory_status (PropID,CurrentLocation,CurrentStatus,AcquisitionCost,Notes) VALUES (%s,%s,%s,%s,%s)", (prop_id, data.get("CurrentLocation"), data["CurrentStatus"], data.get("AcquisitionCost") or None, data.get("InventoryNotes") or "Updated from prop editor")))
            if production_id:
                statements.append(("INSERT INTO production_props (ProductionID,PropID,IsHero) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE IsHero=VALUES(IsHero)", (production_id, prop_id, data.get("Category") == "Hero prop")))
            mysql_store.batch(statements)
            item = mysql_store.query("SELECT * FROM vw_prop_current_status WHERE PropID=%s", (prop_id,))
            if not item: return jsonify({"error": "Prop not found"}), 404
            item[0]["ProductionID"] = production_id
            return jsonify(item[0])
        item = next((p for p in DEMO["props"] if p["PropID"] == prop_id), None)
        if not item: return jsonify({"error": "Prop not found"}), 404
        item.update({k:data.get(k, item.get(k)) for k in ("Name","Description","Category","BaseCondition","CurrentLocation","CurrentStatus")})
        item["LastInventoriedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        if production_id and not any(r["ProductionID"] == production_id and r["PropID"] == prop_id for r in DEMO["production_props"]):
            DEMO["production_props"].append({"ProductionID":production_id,"PropID":prop_id,"IsHero":data.get("Category") == "Hero prop"})
        item["ProductionID"] = production_id or item.get("ProductionID")
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/props/<int:prop_id>")
def delete_prop(prop_id):
    if using_mysql():
        # Clear bridge rows first because assignments deliberately use ON DELETE RESTRICT.
        mysql_store.batch([
            ("DELETE FROM unified_prop_assignments WHERE PropID=%s", (prop_id,)),
            ("DELETE FROM props WHERE PropID=%s", (prop_id,)),
        ])
    else:
        if not any(p["PropID"] == prop_id for p in DEMO["props"]): return jsonify({"error": "Prop not found"}), 404
        DEMO["props"][:] = [p for p in DEMO["props"] if p["PropID"] != prop_id]
        DEMO["production_props"][:] = [r for r in DEMO["production_props"] if r["PropID"] != prop_id]
        DEMO["assignments"][:] = [a for a in DEMO["assignments"] if a["PropID"] != prop_id]
    return "", 204


@app.post("/api/props/<int:prop_id>/inventory")
def update_inventory(prop_id):
    data = payload()
    try:
        need(data, "CurrentStatus")
        if using_mysql():
            mysql_store.write("INSERT INTO prop_inventory_status (PropID,CurrentLocation,CurrentStatus,AcquisitionCost,Notes) VALUES (%s,%s,%s,%s,%s)", (prop_id, data.get("CurrentLocation"), data["CurrentStatus"], data.get("AcquisitionCost") or None, data.get("Notes")))
            item = mysql_store.query("SELECT * FROM vw_prop_current_status WHERE PropID=%s", (prop_id,))[0]
        else:
            item = next((p for p in DEMO["props"] if p["PropID"] == prop_id), None)
            if not item: return jsonify({"error": "Prop not found"}), 404
            item.update({"CurrentStatus": data["CurrentStatus"], "CurrentLocation": data.get("CurrentLocation", item["CurrentLocation"]), "LastInventoriedDate": datetime.now().strftime("%Y-%m-%d %H:%M")})
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.get("/api/assignments")
def assignments():
    scene_id = request.args.get("scene_id", type=int)
    if using_mysql():
        sql = """SELECT a.*, p.Name AS PropName, p.Category AS PropCategory, c.Name AS CharacterName,
            cur.CurrentStatus, cur.CurrentLocation FROM unified_prop_assignments a
            JOIN props p ON p.PropID=a.PropID LEFT JOIN characters c ON c.CharacterID=a.CharacterID
            LEFT JOIN vw_prop_current_status cur ON cur.PropID=a.PropID"""
        params: tuple = ()
        if scene_id: sql += " WHERE a.SceneID=%s"; params = (scene_id,)
        rows = mysql_store.query(sql + " ORDER BY a.IsRequired DESC, p.Name", params)
    else:
        rows = DEMO["assignments"] if not scene_id else [a for a in DEMO["assignments"] if a["SceneID"] == scene_id]
        rows = decorate_demo_assignments(rows)
    return jsonify(rows)


@app.post("/api/assignments")
def create_assignment():
    data = payload()
    try:
        need(data, "SceneID", "PropID", "UsageType")
        char_id = data.get("CharacterID") or None
        if using_mysql():
            new_id = mysql_store.write("""INSERT INTO unified_prop_assignments (SceneID,PropID,CharacterID,IsRequired,UsageType,PlacementNotes,ActorContext,TimeCode,PropPhotoPath)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (data["SceneID"], data["PropID"], char_id, bool(data.get("IsRequired", True)), data["UsageType"], data.get("PlacementNotes"), data.get("ActorContext"), data.get("TimeCode"), data.get("PropPhotoPath")))
            item = mysql_store.query("""SELECT a.*,p.Name PropName,p.Category PropCategory,c.Name CharacterName,cur.CurrentStatus,cur.CurrentLocation
                FROM unified_prop_assignments a JOIN props p ON p.PropID=a.PropID LEFT JOIN characters c ON c.CharacterID=a.CharacterID LEFT JOIN vw_prop_current_status cur ON cur.PropID=a.PropID WHERE a.AssignmentID=%s""", (new_id,))[0]
        else:
            item = {"AssignmentID": demo_next("assignments", "AssignmentID"), "SceneID": int(data["SceneID"]), "PropID": int(data["PropID"]), "CharacterID": int(char_id) if char_id else None, "IsRequired": int(bool(data.get("IsRequired", True))), "UsageType": data["UsageType"], "PlacementNotes": data.get("PlacementNotes"), "ActorContext": data.get("ActorContext"), "TimeCode": data.get("TimeCode")}
            DEMO["assignments"].append(item); item = decorate_demo_assignments([item])[0]
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/assignments/<int:assignment_id>")
def update_assignment(assignment_id):
    data = payload()
    try:
        need(data, "SceneID", "PropID", "UsageType")
        char_id = data.get("CharacterID") or None
        if using_mysql():
            mysql_store.write("""UPDATE unified_prop_assignments SET SceneID=%s, PropID=%s, CharacterID=%s, IsRequired=%s,
                UsageType=%s, PlacementNotes=%s, ActorContext=%s, TimeCode=%s, PropPhotoPath=%s WHERE AssignmentID=%s""", (data["SceneID"], data["PropID"], char_id, bool(data.get("IsRequired", True)), data["UsageType"], data.get("PlacementNotes"), data.get("ActorContext"), data.get("TimeCode"), data.get("PropPhotoPath"), assignment_id))
            item = mysql_store.query("""SELECT a.*,p.Name PropName,p.Category PropCategory,c.Name CharacterName,cur.CurrentStatus,cur.CurrentLocation
                FROM unified_prop_assignments a JOIN props p ON p.PropID=a.PropID LEFT JOIN characters c ON c.CharacterID=a.CharacterID LEFT JOIN vw_prop_current_status cur ON cur.PropID=a.PropID WHERE a.AssignmentID=%s""", (assignment_id,))
            if not item: return jsonify({"error": "Assignment not found"}), 404
            return jsonify(item[0])
        item = next((a for a in DEMO["assignments"] if a["AssignmentID"] == assignment_id), None)
        if not item: return jsonify({"error": "Assignment not found"}), 404
        item.update({"SceneID":int(data["SceneID"]), "PropID":int(data["PropID"]), "CharacterID":int(char_id) if char_id else None, "IsRequired":int(bool(data.get("IsRequired", True))), "UsageType":data["UsageType"], "PlacementNotes":data.get("PlacementNotes"), "ActorContext":data.get("ActorContext"), "TimeCode":data.get("TimeCode"), "PropPhotoPath":data.get("PropPhotoPath")})
        return jsonify(decorate_demo_assignments([item])[0])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/assignments/<int:assignment_id>")
def delete_assignment(assignment_id):
    if using_mysql():
        mysql_store.write("DELETE FROM unified_prop_assignments WHERE AssignmentID=%s", (assignment_id,))
    else:
        DEMO["assignments"][:] = [a for a in DEMO["assignments"] if a["AssignmentID"] != assignment_id]
    return "", 204


@app.get("/api/logs")
def logs():
    scene_id = request.args.get("scene_id", type=int)
    production_id = request.args.get("production_id", type=int)
    if using_mysql():
        sql = """SELECT l.*, s.SceneNumber, s.Setting FROM scene_continuity_logs l
             JOIN scenes s ON s.SceneID=l.SceneID"""
        conditions: list[str] = []
        params: list[int] = []
        if scene_id:
            conditions.append("l.SceneID=%s"); params.append(scene_id)
        if production_id:
            conditions.append("s.ProductionID=%s"); params.append(production_id)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        rows = mysql_store.query(sql + " ORDER BY l.Timestamp DESC LIMIT 60", tuple(params))
    else:
        scene_map = {s["SceneID"]: s for s in DEMO["scenes"]}
        valid_scene_ids = {s["SceneID"] for s in DEMO["scenes"] if not production_id or s["ProductionID"] == production_id}
        rows = [copy.deepcopy(x) for x in DEMO["logs"] if x["SceneID"] in valid_scene_ids and (not scene_id or x["SceneID"] == scene_id)]
        for l in rows:
            scene = scene_map.get(l["SceneID"], {})
            l.update({"SceneNumber": scene.get("SceneNumber"), "Setting": scene.get("Setting")})
        rows.sort(key=lambda x: x["Timestamp"], reverse=True)
    return jsonify(rows)


@app.post("/api/logs")
def create_log():
    data = payload()
    try:
        need(data, "SceneID", "TakeNumber", "ContinuityIssues", "ActionTaken")
        if using_mysql():
            new_id = mysql_store.write("INSERT INTO scene_continuity_logs (SceneID,TakeNumber,ContinuityIssues,ActionTaken,SceneNotes) VALUES (%s,%s,%s,%s,%s)", (data["SceneID"], data["TakeNumber"], data["ContinuityIssues"], data["ActionTaken"], data.get("SceneNotes")))
            item = mysql_store.query("""SELECT l.*,s.SceneNumber,s.Setting FROM scene_continuity_logs l JOIN scenes s ON s.SceneID=l.SceneID WHERE l.LogID=%s""", (new_id,))[0]
        else:
            s = next((s for s in DEMO["scenes"] if s["SceneID"] == int(data["SceneID"])), {})
            item = {"LogID": demo_next("logs", "LogID"), "SceneID": int(data["SceneID"]), "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "TakeNumber": data["TakeNumber"], "ContinuityIssues": data["ContinuityIssues"], "ActionTaken": data["ActionTaken"], "SceneNotes": data.get("SceneNotes"), "SceneNumber": s.get("SceneNumber"), "Setting": s.get("Setting")}
            DEMO["logs"].append(item)
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/api/logs/<int:log_id>")
def update_log(log_id):
    data = payload()
    try:
        need(data, "SceneID", "TakeNumber", "ContinuityIssues", "ActionTaken")
        if using_mysql():
            mysql_store.write("UPDATE scene_continuity_logs SET SceneID=%s, TakeNumber=%s, ContinuityIssues=%s, ActionTaken=%s, SceneNotes=%s WHERE LogID=%s", (data["SceneID"], data["TakeNumber"], data["ContinuityIssues"], data["ActionTaken"], data.get("SceneNotes"), log_id))
            item = mysql_store.query("SELECT l.*,s.SceneNumber,s.Setting FROM scene_continuity_logs l JOIN scenes s ON s.SceneID=l.SceneID WHERE l.LogID=%s", (log_id,))
            if not item: return jsonify({"error": "Continuity log not found"}), 404
            return jsonify(item[0])
        item = next((l for l in DEMO["logs"] if l["LogID"] == log_id), None)
        if not item: return jsonify({"error": "Continuity log not found"}), 404
        s = next((s for s in DEMO["scenes"] if s["SceneID"] == int(data["SceneID"])), {})
        item.update({"SceneID":int(data["SceneID"]), "TakeNumber":data["TakeNumber"], "ContinuityIssues":data["ContinuityIssues"], "ActionTaken":data["ActionTaken"], "SceneNotes":data.get("SceneNotes"), "SceneNumber":s.get("SceneNumber"), "Setting":s.get("Setting")})
        return jsonify(item)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/logs/<int:log_id>")
def delete_log(log_id):
    if using_mysql():
        mysql_store.write("DELETE FROM scene_continuity_logs WHERE LogID=%s", (log_id,))
    else:
        if not any(l["LogID"] == log_id for l in DEMO["logs"]): return jsonify({"error": "Continuity log not found"}), 404
        DEMO["logs"][:] = [l for l in DEMO["logs"] if l["LogID"] != log_id]
    return "", 204


@app.get("/api/dashboard")
def dashboard():
    production_id = request.args.get("production_id", type=int) or 1
    if using_mysql():
        metrics = mysql_store.query("""SELECT
            (SELECT COUNT(*) FROM scenes WHERE ProductionID=%s) AS SceneCount,
            (SELECT COUNT(*) FROM unified_prop_assignments a JOIN scenes s ON s.SceneID=a.SceneID WHERE s.ProductionID=%s) AS AssignmentCount,
            (SELECT COUNT(DISTINCT a.PropID) FROM unified_prop_assignments a JOIN scenes s ON s.SceneID=a.SceneID WHERE s.ProductionID=%s) AS PropCount,
            (SELECT COUNT(DISTINCT a.PropID) FROM unified_prop_assignments a JOIN scenes s ON s.SceneID=a.SceneID JOIN vw_prop_current_status p ON p.PropID=a.PropID WHERE s.ProductionID=%s AND p.CurrentStatus IN ('Missing','Broken')) AS AlertCount""", (production_id, production_id, production_id, production_id))[0]
        readiness = mysql_store.query("SELECT * FROM vw_scene_readiness WHERE ProductionID=%s ORDER BY SceneNumber LIMIT 5", (production_id,))
        recent = mysql_store.query("""SELECT l.*,s.SceneNumber,s.Setting FROM scene_continuity_logs l JOIN scenes s ON s.SceneID=l.SceneID
            WHERE s.ProductionID=%s ORDER BY l.Timestamp DESC LIMIT 5""", (production_id,))
        alerts = mysql_store.query("""SELECT DISTINCT p.* FROM vw_prop_current_status p JOIN unified_prop_assignments a ON a.PropID=p.PropID JOIN scenes s ON s.SceneID=a.SceneID
            WHERE s.ProductionID=%s AND p.CurrentStatus IN ('Missing','Broken') ORDER BY p.CurrentStatus,p.Name""", (production_id,))
    else:
        scenes_for = [s for s in DEMO["scenes"] if s["ProductionID"] == production_id]
        ids = {s["SceneID"] for s in scenes_for}; assigns = [a for a in DEMO["assignments"] if a["SceneID"] in ids]
        assigned_props = {a["PropID"] for a in assigns}; alerts = [p for p in DEMO["props"] if p["PropID"] in assigned_props and p["CurrentStatus"] in ("Missing", "Broken")]
        metrics = {"SceneCount": len(scenes_for), "AssignmentCount": len(assigns), "PropCount": len(assigned_props), "AlertCount": len(alerts)}
        readiness = []
        for s in scenes_for:
            a = [a for a in assigns if a["SceneID"] == s["SceneID"]]
            readiness.append({**s, "TotalAssignments": len(a), "RequiredProps": sum(x["IsRequired"] for x in a), "AvailableProps": sum(1 for x in a if next((p for p in DEMO["props"] if p["PropID"] == x["PropID"]), {}).get("CurrentStatus") == "Available"), "AtRiskProps": sum(1 for x in a if next((p for p in DEMO["props"] if p["PropID"] == x["PropID"]), {}).get("CurrentStatus") in ("Missing", "Broken"))})
        recent = sorted([dict(x, **{"SceneNumber": next(s["SceneNumber"] for s in DEMO["scenes"] if s["SceneID"] == x["SceneID"]), "Setting": next(s["Setting"] for s in DEMO["scenes"] if s["SceneID"] == x["SceneID"])}) for x in DEMO["logs"]], key=lambda x:x["Timestamp"], reverse=True)[:5]
    return app.response_class(response=app.json.dumps({"metrics": metrics, "readiness": readiness, "recent": recent, "alerts": alerts}, default=json_default), status=200, mimetype="application/json")


@app.get("/api/schema")
def schema():
    return jsonify({
        "entities": [
            {"name": "productions", "role": "Production master", "fields": "ProductionID, Title, Director, dates, budget, status"},
            {"name": "scenes", "role": "Script breakdown", "fields": "SceneID, ProductionID, SceneNumber, setting, pages"},
            {"name": "props", "role": "Digital prop closet", "fields": "PropID, name, category, condition"},
            {"name": "production_props", "role": "Production asset scope", "fields": "ProductionID, PropID, hero flag"},
            {"name": "production_characters", "role": "Production cast scope", "fields": "ProductionID, CharacterID, billing order"},
            {"name": "unified_prop_assignments", "role": "Core bridge", "fields": "SceneID, PropID, CharacterID, usage, placement"},
            {"name": "prop_inventory_status", "role": "Inventory audit", "fields": "PropID, status, location, cost, timestamp"},
            {"name": "scene_continuity_logs", "role": "Continuity history", "fields": "SceneID, take, issue, action, notes"},
            {"name": "digital_assets_library", "role": "Asset references", "fields": "AssetID, PropID, format, version, path"}
        ],
        "relationships": ["Productions 1—∞ Scenes", "Productions ∞—∞ Characters via production_characters", "Productions ∞—∞ Props via production_props", "Scenes ∞—∞ Props via unified_prop_assignments", "Characters 1—∞ unified_prop_assignments", "Props 1—∞ inventory status / digital assets", "Scenes 1—∞ continuity logs"]
    })


@app.errorhandler(Exception)
def handle_error(error):
    # Preserve validation/HTTP errors handled by Flask; return a useful API message for DB errors.
    from werkzeug.exceptions import HTTPException
    if isinstance(error, HTTPException):
        return error
    app.logger.exception("Unhandled request error")
    return jsonify({"error": "Database request failed", "detail": str(error) if app.debug else "Check MySQL configuration and schema."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # The Windows launcher enables this optional convenience flag.
    if os.getenv("OPEN_BROWSER", "").lower() in {"1", "true", "yes"}:
        import threading
        import webbrowser
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
