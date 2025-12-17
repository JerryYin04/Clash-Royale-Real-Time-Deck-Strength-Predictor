CREATE DATABASE IF NOT EXISTS `clash_royale`;
USE `clash_royale`;
CREATE TABLE IF NOT EXISTS `clash_royale_cards` (
id INT AUTO_INCREMENT PRIMARY KEY,
`name` VARCHAR(128),
maxEvolutionLevel TINYINT,
elixirCost TINYINT,
rarity VARCHAR(64),
iconUrls TEXT,
evolutionIcons TEXT,
card_type VARCHAR(64),
mobility VARCHAR(64),
targets VARCHAR(64),
attack_type VARCHAR(64),
groupCard VARCHAR(64),
`usage` FLOAT,
hitpoints INT
);
LOAD DATA LOCAL INFILE '/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_cards_clean.csv'
INTO TABLE clash_royale_cards
CHARACTER SET utf8
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@name, @maxEvolutionLevel, @elixirCost, @iconUrls, @evolutionIcons, @rarity, 
@type, @mobility, @targets, @attack_type, @groupCard, @usage, @hitpoints)
SET
    `name` = @name,
    maxEvolutionLevel = @maxEvolutionLevel, 
    elixirCost = @elixirCost,
    iconUrls = @iconUrls,
    evolutionIcons = @evolutionIcons,
    rarity = @rarity,
    card_type = @type,
    mobility = @mobility,
    targets = @targets,
    attack_type = @attack_type,
    groupCard = @groupCard,
    `usage` = @usage,
    hitpoints = @hitpoints;
LOAD DATA LOCAL INFILE '/Users/yinweitang/Desktop/Code Projects/Clash Royale Decks/Data/clash_royale_decks.csv'
INTO TABLE decks
CHARACTER SET utf8
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@deck_id, @deck_name, @card_name, @deck_win_rate)
SET
    deck_id = @deck_id,
    deck_name = @deck_name,
    card_name = @card_name,
    deck_win_rate = @deck_win_rate;
    
WITH deck_info AS (
    SELECT DISTINCT
        deck_id,
        deck_name,
        deck_win_rate
    FROM decks
),
deck_cards AS (
    SELECT
        d.deck_id,
        AVG(c.elixirCost) AS avg_elixirCost,
        AVG(c.usage) AS avg_card_usage,
        SUM(IFNULL(c.hitpoints,0)) AS total_hitpoints,
        SUM(c.mobility = 'flying' AND c.card_type != 'spell') AS num_air,
        SUM(CASE WHEN c.card_type = 'troop' THEN 1 ELSE 0 END) AS num_troop,
        SUM(CASE WHEN c.card_type = 'spell' THEN 1 ELSE 0 END) AS num_spell,
        SUM(CASE WHEN c.card_type = 'building' THEN 1 ELSE 0 END) AS num_building,
        SUM(CASE WHEN c.targets = 'building'
                  OR c.hitpoints >= 2500
                  OR (c.elixirCost >= 6 AND c.card_type = 'troop')
                 THEN 1 ELSE 0 END) AS num_winconditions,
        SUM(CASE WHEN c.elixirCost <= 3 THEN 1 ELSE 0 END) AS num_cycle_cards,
        SUM(CASE WHEN c.targets = 'both' THEN 1 ELSE 0 END) AS num_air_attackers,
        SUM(CASE WHEN c.attack_type = 'splash' THEN 1 ELSE 0 END) AS num_splash_cards
    FROM decks AS d
    JOIN clash_royale_cards AS c
      ON c.name = d.card_name
    GROUP BY d.deck_id
)
SELECT
    dc.deck_id,
    di.deck_name,
    di.deck_win_rate,
    dc.avg_elixirCost,
    dc.avg_card_usage,
    dc.total_hitpoints,
    dc.num_air,
    dc.num_troop,
    dc.num_spell,
    dc.num_building,
    dc.num_winconditions,
    dc.num_cycle_cards,
    dc.num_air_attackers,
    dc.num_splash_cards
FROM deck_cards AS dc
JOIN deck_info AS di
  ON dc.deck_id = di.deck_id
ORDER BY dc.deck_id;

