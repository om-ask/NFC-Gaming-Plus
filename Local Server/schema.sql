PRAGMA foreign_keys = ON;

-- CREATE TABLE IF NOT EXISTS Player (
--     player_id TEXT PRIMARY KEY,
--     player_name TEXT,
--     registeration_time TEXT DEFAULT (datetime('now'))
-- );


CREATE TABLE IF NOT EXISTS Visitor (
    visitor_id TEXT PRIMARY KEY,
    visitor_name TEXT,
    registeration_time TEXT DEFAULT (datetime('now'))
);

-- renamed to Quest
-- CREATE TABLE IF NOT EXISTS Place (
--     place_id TEXT PRIMARY KEY,
--     points_visiting_now INTEGER
-- );



CREATE TABLE IF NOT EXISTS Quest (
    quest_id TEXT PRIMARY KEY,
    quest_name TEXT,
    points_visiting_now INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS PointRecords (
    visitor_id TEXT,
    quest_id TEXT,
    points INTEGER,
    time_visited TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (visitor_id, quest_id),
    FOREIGN KEY (visitor_Id) REFERENCES Visitor(visitor_id),
    FOREIGN KEY (quest_id) REFERENCES Place(quest_id)
);

