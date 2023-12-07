 SELECT * FROM users;
-- SELECT * FROM tournaments;
-- DROP TABLE tournaments;
-- SELECT * FROM users_tournaments;
-- DROP TABLE users_tournaments;

-- SET * FROM users WHERE id IN (SELECT player_id FROM users_tournaments WHERE tournament_id = 1) AND id IN (SELECT partner_id FROM users_tournaments WHERE tournament_id = 1);

-- SELECT COUNT(player_username) FROM users_tournaments WHERE tournament_id = 1;

SELECT * FROM tournaments;