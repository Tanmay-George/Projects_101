# CONTINUITY — Digital Prop Closet & Scene Tracker

A DBMS project web application based on the supplied ER diagram. It turns the data model into a professional production-intelligence workspace: scenes, props, character context, inventory audits, digital assets, and take-by-take continuity notes all share a normalized relational model. The supplied demonstration records are an academic continuity study of the final Mahishmati battle sequence in *Baahubali 2: The Conclusion*; all tracker labels, breakdown notes, and sample workflow data are original project content.

## Interface and record management

The application uses a responsive **Studio Console** structure: a control room overview, a compact scene readiness register, a focused operator rail, and dedicated records screens. Its Art Deco Signal design uses ink charcoal, deep jade, champagne, burgundy, and muted copper. Every primary record type has create, edit, and delete controls:

- **Productions** — switch, create, edit, and delete from the active-production menu.
- **Scenes** — add, edit, open in the placement matrix, or delete from Scene tracker.
- **Prop inventory** — register new assets, update auditable location/status snapshots, edit full asset metadata, or delete an asset and its linked placements.
- **Placement matrix** — add, edit, and remove scene × prop × character assignments.
- **Field logs** — add, edit, and delete continuity decisions.
- **Cast & characters** — add, edit, and delete character profiles.

Deletion is always confirmed in the interface. In MySQL mode, the database’s foreign keys and the API’s transaction handling preserve referential integrity.

## Stack

| Layer | Technology |
| --- | --- |
| Front end | HTML5, responsive CSS, vanilla JavaScript |
| Back end | Python 3 + Flask REST API |
| Database | MySQL 8.0+, InnoDB, utf8mb4 |
| Data design | Primary / foreign keys, bridge table, views, stored procedure |

## Project structure

```text
continuity-tracker/
├── app.py                 # Flask server + REST endpoints
├── database/
│   ├── schema.sql         # MySQL DDL, views and stored procedure
│   └── seed.sql           # Demonstration dataset: Baahubali 2 final battle study
├── static/
│   ├── index.html         # Responsive application UI
│   ├── styles.css          # Design system and layouts
│   └── app.js             # UI state, rendering, REST client, CRUD forms
├── .env.example
└── requirements.txt
```

## Database model

The MySQL schema implements the ER diagram as the following tables:

- `productions` → `scenes` is a one-to-many relationship.
- `production_characters` scopes the Cast Registry to the selected production without duplicating character records.
- `production_props` scopes the Asset Inventory to the selected production without duplicating reusable prop records.
- `scenes` and `props` are many-to-many; `unified_prop_assignments` is the bridge table and can also hold a nullable `CharacterID`.
- `props` → `prop_inventory_status` is a one-to-many audit history. The `vw_prop_current_status` view exposes the latest snapshot.
- `props` → `detailed_physical_properties`, `digital_assets_library`, and `detailed_digital_asset_metadata` preserve physical and digital records separately.
- `scenes` → `scene_continuity_logs` is a one-to-many relationship.
- `vw_scene_readiness` delivers an efficient per-scene dashboard summary.
- `sp_log_continuity` is included for controlled continuity-log inserts in MySQL.

## Quick start on Windows

1. Extract the ZIP file completely (do **not** run it while it is still compressed).
2. Open the extracted `continuity-tracker` folder.
3. Double-click **`Run_Continuity_Tracker.bat`**.
4. On first use it creates its own Python environment, installs the required packages, starts the server, and opens the tracker at `http://127.0.0.1:5000`.

Python 3.10 or newer must be installed. Without a `.env` file it opens in its built-in demo mode immediately. For fully persistent project records, configure MySQL using the steps below.

## Run with MySQL (submission mode)

### 1. Create the schema and sample data

From the project directory, run:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

> If your MySQL account does not have permission to create databases, create `continuity_tracker` manually, select it with `USE continuity_tracker;`, and then execute the rest of each SQL file.

### 2. Set environment variables

```bash
cp .env.example .env
```

Edit `.env` with your local MySQL credentials and keep `APP_MODE=mysql`.

### 3. Install and start the application

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## Demo mode

If MySQL is not yet available, set `APP_MODE=demo`, or omit the `.env` file. The same Flask REST endpoints serve a supplied in-memory sample so the frontend can be evaluated. The left sidebar clearly reports **DEMO PREVIEW**; changes last only while the server runs. For persistent project data, use MySQL submission mode.

## REST API summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET/POST` | `/api/productions` | Manage productions |
| `GET/POST` | `/api/scenes?production_id=1` | Script breakdown scenes |
| `GET/POST` | `/api/props` | Prop closet |
| `POST` | `/api/props/:id/inventory` | Append an inventory snapshot |
| `GET/POST` | `/api/assignments?scene_id=1` | Scene × prop assignment bridge |
| `DELETE` | `/api/assignments/:id` | Remove an assignment |
| `GET/POST` | `/api/logs?scene_id=1` | Continuity notes |
| `GET` | `/api/dashboard?production_id=1` | Dashboard aggregates |
| `GET` | `/api/schema` | ER implementation metadata |

## Suggested DBMS demonstration flow

1. Start with **Schema map** and explain how the assignment table solves the `Scenes ↔ Props` many-to-many relationship.
2. In **Prop inventory**, update the status of a prop. The app adds a new row to `prop_inventory_status` instead of overwriting history.
3. In **Assignments**, attach a prop to a scene and explain the character and placement attributes.
4. In **Continuity log**, create a take note. The dashboard will show the new field note immediately.
5. In MySQL, show the normalized data and views:

```sql
USE continuity_tracker;
SELECT * FROM vw_prop_current_status;
SELECT * FROM vw_scene_readiness;
SELECT * FROM unified_prop_assignments;
```
