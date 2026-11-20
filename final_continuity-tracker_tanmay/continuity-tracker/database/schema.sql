-- CONTINUITY: Digital Prop Closet & Scene Tracker
-- MySQL 8.0+ schema derived from the supplied ER diagram.

CREATE DATABASE IF NOT EXISTS continuity_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE continuity_tracker;

CREATE TABLE IF NOT EXISTS productions (
  ProductionID INT AUTO_INCREMENT PRIMARY KEY,
  Title VARCHAR(160) NOT NULL,
  Director VARCHAR(120),
  StartDate DATE,
  EndDate DATE,
  Status ENUM('Pre-production', 'In production', 'Post-production', 'Wrapped') DEFAULT 'Pre-production',
  ProductionBudget DECIMAL(14,2) DEFAULT 0,
  Notes TEXT,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scenes (
  SceneID INT AUTO_INCREMENT PRIMARY KEY,
  ProductionID INT NOT NULL,
  SceneNumber VARCHAR(30) NOT NULL,
  Description TEXT,
  Setting VARCHAR(180),
  TimeOfDay ENUM('Dawn', 'Day', 'Dusk', 'Night', 'Continuous', 'Unknown') DEFAULT 'Unknown',
  Pages DECIMAL(5,2),
  ScriptPageStart DECIMAL(6,2),
  ScriptPageEnd DECIMAL(6,2),
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uq_scene_number_per_production UNIQUE (ProductionID, SceneNumber),
  CONSTRAINT fk_scenes_production FOREIGN KEY (ProductionID)
    REFERENCES productions(ProductionID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS characters (
  CharacterID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(120) NOT NULL,
  ActorName VARCHAR(120),
  Notes TEXT,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS props (
  PropID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(140) NOT NULL,
  Description TEXT,
  Category VARCHAR(80),
  BaseCondition ENUM('Pristine', 'Good', 'Aged', 'Damaged', 'Hero / Fragile') DEFAULT 'Good',
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Production scoping bridges. A cast member or reusable asset can be linked to one
-- or more productions without duplicating the master character/prop record.
CREATE TABLE IF NOT EXISTS production_characters (
  ProductionID INT NOT NULL,
  CharacterID INT NOT NULL,
  BillingOrder INT NULL,
  ProductionNotes TEXT,
  PRIMARY KEY (ProductionID, CharacterID),
  CONSTRAINT fk_production_characters_production FOREIGN KEY (ProductionID)
    REFERENCES productions(ProductionID) ON DELETE CASCADE,
  CONSTRAINT fk_production_characters_character FOREIGN KEY (CharacterID)
    REFERENCES characters(CharacterID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS production_props (
  ProductionID INT NOT NULL,
  PropID INT NOT NULL,
  IsHero BOOLEAN NOT NULL DEFAULT FALSE,
  ProductionNotes TEXT,
  PRIMARY KEY (ProductionID, PropID),
  CONSTRAINT fk_production_props_production FOREIGN KEY (ProductionID)
    REFERENCES productions(ProductionID) ON DELETE CASCADE,
  CONSTRAINT fk_production_props_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Resolves the many-to-many relationship between scenes, props and (optionally) characters.
CREATE TABLE IF NOT EXISTS unified_prop_assignments (
  AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
  SceneID INT NOT NULL,
  PropID INT NOT NULL,
  CharacterID INT NULL,
  IsRequired BOOLEAN NOT NULL DEFAULT TRUE,
  UsageType VARCHAR(100),
  PlacementNotes TEXT,
  ActorContext VARCHAR(180),
  TimeCode VARCHAR(30),
  PropPhotoPath VARCHAR(500),
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uq_assignment UNIQUE (SceneID, PropID, CharacterID),
  CONSTRAINT fk_assignments_scene FOREIGN KEY (SceneID)
    REFERENCES scenes(SceneID) ON DELETE CASCADE,
  CONSTRAINT fk_assignments_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE RESTRICT,
  CONSTRAINT fk_assignments_character FOREIGN KEY (CharacterID)
    REFERENCES characters(CharacterID) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Snapshot / audit records for a prop. The most recent record is its current state.
CREATE TABLE IF NOT EXISTS prop_inventory_status (
  InventoryLogID INT AUTO_INCREMENT PRIMARY KEY,
  PropID INT NOT NULL,
  CurrentLocation VARCHAR(180),
  CurrentStatus ENUM('Available', 'In Use', 'Missing', 'Broken', 'In Transit', 'Checked Out') DEFAULT 'Available',
  AcquisitionCost DECIMAL(12,2),
  LastInventoriedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
  Notes TEXT,
  CONSTRAINT fk_inventory_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE CASCADE,
  INDEX idx_inventory_prop_date (PropID, LastInventoriedDate DESC)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detailed_physical_properties (
  DetailID INT AUTO_INCREMENT PRIMARY KEY,
  PropID INT NOT NULL UNIQUE,
  Material VARCHAR(120),
  Dimensions VARCHAR(120),
  `Condition` VARCHAR(120),
  Weight VARCHAR(60),
  CONSTRAINT fk_physical_detail_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS digital_assets_library (
  AssetID INT AUTO_INCREMENT PRIMARY KEY,
  PropID INT NOT NULL,
  AssetType VARCHAR(100) NOT NULL,
  FileFormat VARCHAR(30),
  Resolution VARCHAR(60),
  Version VARCHAR(30) DEFAULT 'v1.0',
  FilePath VARCHAR(500),
  Notes TEXT,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_asset_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE CASCADE,
  INDEX idx_assets_prop (PropID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detailed_digital_asset_metadata (
  DetailID INT AUTO_INCREMENT PRIMARY KEY,
  PropID INT NOT NULL,
  PrimaryAssetID INT NULL,
  Keywords VARCHAR(300),
  ColorProfile VARCHAR(80),
  RightsNotes TEXT,
  CONSTRAINT fk_digital_metadata_prop FOREIGN KEY (PropID)
    REFERENCES props(PropID) ON DELETE CASCADE,
  CONSTRAINT fk_digital_metadata_asset FOREIGN KEY (PrimaryAssetID)
    REFERENCES digital_assets_library(AssetID) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scene_continuity_logs (
  LogID INT AUTO_INCREMENT PRIMARY KEY,
  SceneID INT NOT NULL,
  `Timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  TakeNumber VARCHAR(30),
  ContinuityIssues TEXT,
  ActionTaken TEXT,
  SceneNotes TEXT,
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_continuity_scene FOREIGN KEY (SceneID)
    REFERENCES scenes(SceneID) ON DELETE CASCADE,
  INDEX idx_logs_scene_time (SceneID, `Timestamp` DESC)
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW vw_prop_current_status AS
SELECT p.PropID, p.Name, p.Category, p.BaseCondition,
       s.CurrentLocation, s.CurrentStatus, s.LastInventoriedDate
FROM props p
LEFT JOIN prop_inventory_status s ON s.InventoryLogID = (
  SELECT ps.InventoryLogID FROM prop_inventory_status ps
  WHERE ps.PropID = p.PropID
  ORDER BY ps.LastInventoriedDate DESC, ps.InventoryLogID DESC LIMIT 1
);

CREATE OR REPLACE VIEW vw_scene_readiness AS
SELECT s.SceneID, s.ProductionID, s.SceneNumber, s.Setting, s.TimeOfDay,
       COUNT(a.AssignmentID) AS TotalAssignments,
       COALESCE(SUM(a.IsRequired = 1), 0) AS RequiredProps,
       COALESCE(SUM(cur.CurrentStatus = 'Available'), 0) AS AvailableProps,
       COALESCE(SUM(cur.CurrentStatus IN ('Missing','Broken')), 0) AS AtRiskProps
FROM scenes s
LEFT JOIN unified_prop_assignments a ON a.SceneID = s.SceneID
LEFT JOIN vw_prop_current_status cur ON cur.PropID = a.PropID
GROUP BY s.SceneID, s.ProductionID, s.SceneNumber, s.Setting, s.TimeOfDay;

DELIMITER //
CREATE PROCEDURE sp_log_continuity(
  IN p_scene_id INT,
  IN p_take_number VARCHAR(30),
  IN p_issues TEXT,
  IN p_action TEXT,
  IN p_notes TEXT
)
BEGIN
  INSERT INTO scene_continuity_logs (SceneID, TakeNumber, ContinuityIssues, ActionTaken, SceneNotes)
  VALUES (p_scene_id, p_take_number, p_issues, p_action, p_notes);
END //
DELIMITER ;
