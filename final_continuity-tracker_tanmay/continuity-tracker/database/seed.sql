-- Demonstration data for a DBMS continuity breakdown.
-- This is an academic scene/prop analysis of the final Mahishmati confrontation
-- in Baahubali 2: The Conclusion; labels and notes are original tracker records.
USE continuity_tracker;

DELETE FROM detailed_digital_asset_metadata;
DELETE FROM digital_assets_library;
DELETE FROM detailed_physical_properties;
DELETE FROM prop_inventory_status;
DELETE FROM unified_prop_assignments;
DELETE FROM production_characters;
DELETE FROM production_props;
DELETE FROM scene_continuity_logs;
DELETE FROM characters;
DELETE FROM scenes;
DELETE FROM props;
DELETE FROM productions;

INSERT INTO productions (ProductionID, Title, Director, StartDate, EndDate, Status, ProductionBudget, Notes) VALUES
(1, 'Baahubali 2 — Final Battle Continuity Study', 'S. S. Rajamouli', '2017-04-28', '2017-04-28', 'In production', 2500000000.00,
 'Academic continuity breakdown of the final Mahishmati confrontation. Scene labels and production notes are original tracker records, not official screenplay material.');

INSERT INTO scenes (SceneID, ProductionID, SceneNumber, Description, Setting, TimeOfDay, Pages, ScriptPageStart, ScriptPageEnd) VALUES
(1, 1, 'F01', 'Mahendra Baahubali reaches the royal courtyard as the final confrontation begins.', 'Mahishmati palace courtyard', 'Day', 2.00, 1.00, 3.00),
(2, 1, 'F02', 'Bhallaladeva’s royal guard closes the courtyard while Devasena remains within the palace precinct.', 'Mahishmati palace courtyard — eastern gate', 'Day', 2.50, 3.00, 5.50),
(3, 1, 'F03', 'The defenders regroup among the stone pavilions and the royal banners are reset after the first clash.', 'Mahishmati stone pavilion', 'Day', 1.75, 5.50, 7.25),
(4, 1, 'F04', 'Mahendra and Bhallaladeva enter the central arena for the close-quarters duel.', 'Mahishmati royal arena', 'Day', 3.00, 7.25, 10.25),
(5, 1, 'F05', 'The duel moves through the damaged throne approach; weapon condition and hand position must match across coverage.', 'Throne approach and forge platform', 'Day', 2.25, 10.25, 12.50),
(6, 1, 'F06', 'Bhallaladeva is defeated; the courtyard clears for Devasena’s final act of justice.', 'Mahishmati execution courtyard', 'Dusk', 2.00, 12.50, 14.50),
(7, 1, 'F07', 'Aftermath in Mahishmati: the royal standard returns and the new order is witnessed by the court.', 'Mahishmati throne courtyard', 'Dusk', 1.50, 14.50, 16.00);

INSERT INTO characters (CharacterID, Name, ActorName, Notes) VALUES
(1, 'Mahendra Baahubali', 'Prabhas', 'Hero weapon continuity: bow grip, right-hand battle sword, and dust level on armour.'),
(2, 'Bhallaladeva', 'Rana Daggubati', 'Track mace orientation, armour damage, and arena-side entrances.'),
(3, 'Devasena', 'Anushka Shetty', 'Track bow hand-off, costume condition, and position at the execution courtyard.'),
(4, 'Kattappa', 'Sathyaraj', 'Royal guard weapon and shoulder armour remain consistent during courtyard coverage.'),
(5, 'Bijjaladeva', 'Nassar', 'Court witness context for aftermath and throne-courtyard reaction coverage.');

INSERT INTO props (PropID, Name, Description, Category, BaseCondition) VALUES
(1, 'Baahubali hero bow', 'Carved dark-wood hero bow used for Mahendra’s courtyard coverage.', 'Hero prop', 'Aged'),
(2, 'Bhallaladeva war mace', 'Large iron-finish mace with controlled battle scuffs for the central duel.', 'Hero prop', 'Aged'),
(3, 'Mahendra battle sword', 'Hero sword with dulled camera-safe edge and marked right-hand grip.', 'Hero prop', 'Aged'),
(4, 'Devasena bow', 'Ceremonial bow used in palace precinct and execution-courtyard coverage.', 'Hero prop', 'Aged'),
(5, 'Royal standard — Mahishmati', 'Gold-edged royal banner; tear pattern must remain camera-left after F03.', 'Set dressing', 'Damaged'),
(6, 'Forged iron chain', 'Arena chain section used for the throne-approach and forge-platform action.', 'Hand prop', 'Aged'),
(7, 'Royal guard shield', 'Embossed bronze shield for Kattappa and royal guard foreground action.', 'Hand prop', 'Damaged'),
(8, 'Arena fire brazier', 'Controlled flame brazier for the execution-courtyard transition.', 'Set dressing', 'Aged'),
(9, 'Throne court seal', 'Brass royal seal placed on the aftermath dais.', 'Set dressing', 'Good'),
(10, 'Bhallaladeva armour plate', 'Removable left shoulder armour plate with progressive battle damage.', 'Costume accessory', 'Damaged');

INSERT INTO production_characters (ProductionID, CharacterID, BillingOrder, ProductionNotes) VALUES
(1, 1, 1, 'Hero lead for the final battle continuity study.'),
(1, 2, 2, 'Primary opponent; damage and weapon progression is tracked.'),
(1, 3, 3, 'Execution-courtyard and palace-precinct continuity context.'),
(1, 4, 4, 'Guard-line and foreground defence context.'),
(1, 5, 5, 'Aftermath court witness context.');

INSERT INTO production_props (ProductionID, PropID, IsHero, ProductionNotes) VALUES
(1, 1, TRUE, 'Mahendra hero bow'),
(1, 2, TRUE, 'Bhallaladeva hero mace'),
(1, 3, TRUE, 'Mahendra hero sword'),
(1, 4, TRUE, 'Devasena hero bow'),
(1, 5, FALSE, 'Royal background standard'),
(1, 6, TRUE, 'Marked forge-platform action chain'),
(1, 7, FALSE, 'Royal guard foreground shield'),
(1, 8, FALSE, 'Execution-courtyard flame dressing'),
(1, 9, FALSE, 'Aftermath dais detail'),
(1, 10, FALSE, 'Bhallaladeva armour damage component');

INSERT INTO prop_inventory_status (PropID, CurrentLocation, CurrentStatus, AcquisitionCost, LastInventoriedDate, Notes) VALUES
(1, 'Hero rack · Arena unit', 'In Use', 42000.00, '2017-04-28 07:10:00', 'Lower limb points camera-right on F01 entry.'),
(2, 'Bhallaladeva stand-in case', 'In Use', 66000.00, '2017-04-28 07:12:00', 'Head low beside right boot at F04 reset.'),
(3, 'Hero rack · Arena unit', 'Available', 38000.00, '2017-04-28 07:08:00', 'Camera-safe edge checked.'),
(4, 'Devasena prop station', 'Available', 26000.00, '2017-04-28 07:04:00', 'Keep at left side for eastern-gate coverage.'),
(5, 'Stone pavilion reset cart', 'Available', 18000.00, '2017-04-28 06:55:00', 'Torn edge marked camera-left.'),
(6, 'Forge platform · marked position', 'In Use', 9000.00, '2017-04-28 07:15:00', 'Marked link must stay visible near wrist.'),
(7, 'Guard cart · bay 2', 'Available', 15000.00, '2017-04-28 07:00:00', 'Embossed face toward camera.'),
(8, 'Safety hold · courtyard west', 'Broken', 22000.00, '2017-04-28 06:50:00', 'Ignition inconsistent; matching flame unit required.'),
(9, 'Court detail case', 'Available', 7200.00, '2017-04-28 06:58:00', 'Emblem faces audience side.'),
(10, 'Costume repair tent', 'Missing', 17500.00, '2017-04-28 07:06:00', 'Deep scrape reference B-10 pending repair.');

INSERT INTO detailed_physical_properties (PropID, Material, Dimensions, `Condition`, Weight) VALUES
(1, 'Dark hardwood, leather grip', '168 × 4 × 3 cm', 'Aged finish; grip marked', '1.2 kg'),
(2, 'Iron-finish resin core', '92 × 24 × 22 cm', 'Controlled battle scuffs', '5.8 kg'),
(3, 'Aluminium hero blade, leather grip', '98 × 8 × 3 cm', 'Dulled camera-safe edge', '1.6 kg'),
(4, 'Carved wood, gold paint', '142 × 4 × 3 cm', 'Aged ceremonial finish', '0.9 kg'),
(5, 'Silk blend, embroidered trim', '260 × 110 cm', 'Torn lower edge', '0.7 kg'),
(6, 'Rubber-coated chain links', '190 cm section', 'Marked action link', '4.2 kg'),
(9, 'Brass', '12 × 12 × 3 cm', 'Polished emblem face', '0.8 kg'),
(10, 'Foam armour, metallic finish', '31 × 26 × 8 cm', 'Deep left-side scrape', '0.6 kg');

INSERT INTO digital_assets_library (AssetID, PropID, AssetType, FileFormat, Resolution, Version, FilePath, Notes) VALUES
(1, 1, 'Reference photo', 'JPG', '6000 × 4000', 'v1.2', '/assets/baahubali/bow/entry-right.jpg', 'F01 hero bow entry reference.'),
(2, 2, 'Reference photo', 'JPG', '6000 × 4000', 'v2.0', '/assets/baahubali/mace/right-hand-low.jpg', 'F04 mace hand/orientation reference.'),
(3, 5, 'Continuity photo', 'JPG', '6000 × 4000', 'v1.1', '/assets/baahubali/standard/torn-left.jpg', 'F03 torn standard reset image.'),
(4, 10, 'Damage reference', 'PNG', '4096 × 4096', 'v1.0', '/assets/baahubali/armour/plate-b10.png', 'Progressive armour scrape reference.'),
(5, 9, 'Reference photo', 'JPG', '6000 × 4000', 'v1.0', '/assets/baahubali/seal/dais-center.jpg', 'Aftermath dais placement reference.');

INSERT INTO detailed_digital_asset_metadata (PropID, PrimaryAssetID, Keywords, ColorProfile, RightsNotes) VALUES
(1, 1, 'bow, hero, Mahendra, courtyard, entry', 'sRGB', 'Academic project reference record.'),
(2, 2, 'mace, Bhallaladeva, duel, right hand', 'sRGB', 'Academic project reference record.'),
(5, 3, 'standard, banner, torn, pavilion', 'sRGB', 'Academic project reference record.'),
(10, 4, 'armour, plate, scrape, battle damage', 'Adobe RGB', 'Academic project reference record.'),
(9, 5, 'seal, brass, dais, aftermath', 'sRGB', 'Academic project reference record.');

INSERT INTO unified_prop_assignments (AssignmentID, SceneID, PropID, CharacterID, IsRequired, UsageType, PlacementNotes, ActorContext, TimeCode, PropPhotoPath) VALUES
(1, 1, 1, 1, TRUE, 'Holding', 'Mahendra enters with bow in left hand; lower limb faces camera right.', 'Mahendra establishes the confrontation.', '00:00:14', '/assets/baahubali/bow/entry-right.jpg'),
(2, 1, 5, NULL, TRUE, 'Placed', 'Royal standard at north arcade, intact before the first clash.', 'Background story marker.', '00:00:28', NULL),
(3, 2, 4, 3, TRUE, 'Holding', 'Devasena keeps bow at her left side inside the eastern gate.', 'Devasena observes the guard movement.', '00:01:06', NULL),
(4, 2, 7, 4, TRUE, 'Holding', 'Shield face toward camera for the guard foreground reset.', 'Kattappa holds the defensive line.', '00:01:21', NULL),
(5, 3, 5, NULL, TRUE, 'Placed', 'Torn edge now hangs camera-left after impact coverage.', 'Stone pavilion continuity.', '00:02:02', '/assets/baahubali/standard/torn-left.jpg'),
(6, 4, 2, 2, TRUE, 'Handling', 'Mace begins in Bhallaladeva’s right hand, head low beside his boot.', 'Central arena duel.', '00:03:10', '/assets/baahubali/mace/right-hand-low.jpg'),
(7, 4, 3, 1, TRUE, 'Holding', 'Sword begins in Mahendra’s right hand; guard faces outward.', 'Central arena duel.', '00:03:12', NULL),
(8, 5, 6, 1, TRUE, 'Handling', 'Chain enters from forge platform, marked link remains visible near wrist.', 'Throne approach action beat.', '00:04:04', NULL),
(9, 5, 10, 2, TRUE, 'Worn', 'Left shoulder plate has deep scrape facing camera after the fall.', 'Bhallaladeva damage progression.', '00:04:18', '/assets/baahubali/armour/plate-b10.png'),
(10, 6, 8, NULL, TRUE, 'Placed', 'Brazier at courtyard west; flame height matches dusk plate.', 'Execution-courtyard atmosphere.', '00:05:12', NULL),
(11, 6, 4, 3, FALSE, 'Carried', 'Bow carried down at Devasena’s left side.', 'Devasena enters final justice beat.', '00:05:23', NULL),
(12, 7, 9, 5, TRUE, 'Placed', 'Seal is centered on the aftermath dais, emblem facing audience side.', 'Court restoration image.', '00:06:02', '/assets/baahubali/seal/dais-center.jpg'),
(13, 7, 5, NULL, TRUE, 'Placed', 'Standard is repaired and raised at north arcade for the final image.', 'New-order visual cue.', '00:06:18', NULL);

INSERT INTO scene_continuity_logs (SceneID, `Timestamp`, TakeNumber, ContinuityIssues, ActionTaken, SceneNotes) VALUES
(4, '2017-04-28 09:18:00', 'F04 · Take 6', 'Bhallaladeva’s mace returned to the left hand after the reverse-angle cut.', 'Reset mace to right hand with head low beside the boot; photographed before action.', 'Mahendra sword guard remains outward.'),
(5, '2017-04-28 09:06:00', 'F05 · Take 3', 'Left shoulder armour plate was missing the deep scrape from the previous setup.', 'Sent armour plate to costume repair tent and held close coverage.', 'Use damage reference card B-10.'),
(3, '2017-04-28 08:42:00', 'F03 · Take 4', 'Royal standard tear was reversed after pavilion reset.', 'Restored torn edge to camera-left and marked reset cart.', 'Banner must remain torn until F06 clearance.'),
(6, '2017-04-28 08:21:00', 'F06 · Take 2', 'Brazier ignition was inconsistent with the dusk atmosphere plate.', 'Flagged brazier for safety check; prepared matching flame unit.', 'Devasena bow remains lowered on entry.');
