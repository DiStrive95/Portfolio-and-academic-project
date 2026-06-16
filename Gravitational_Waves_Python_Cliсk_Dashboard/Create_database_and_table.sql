-- Создаём БД
CREATE DATABASE IF NOT EXISTS gw;

-- Учитывая структуру, которую видно в json или в csv, создаём таблицу, в которую всё загрузим.
CREATE TABLE gw.events (
	common_name String, 					-- имя события
	gps Float64, 							-- время события в формате GPS (особый счёт секунд, принятый в астрономии)
	mass_1_source Nullable(Float32), 		-- масса первого объекта
	mass_2_source Nullable(Float32), 		-- масса второго объекта
	total_mass_source Nullable(Float32), 	-- суммарная масса системы
	network_snr Nullable(Float32), 			-- отношение сигнал/шум: насколько уверенно детекторы поймали событие
	luminosity_distance Nullable(Float32),	-- расстояние до источника в мегапарсеках (Mpc)
	redshift Nullable(Float32),				-- красное смещение, мера удалённости источника
	catalog Nullable(String),				-- из какого наблюдательного прогона событие 
	merger_type String,						-- тип слияния
	_load_at DateTime DEFAULT now()			-- когда запись попала в базу, проставляется автоматически
) ENGINE = MergeTree()
ORDER BY common_name;

-- Следующие две команды проверяют, что таблица создана и она пустая.
DESCRIBE TABLE gw.events;

SELECT
	COUNT()
FROM gw.events;
--Далее работа проводится в python-скрипте load.


-- Проверяем содержание таблицы.
SELECT 
	common_name,
	mass_1_source,
	mass_2_source,
	merger_type,
	luminosity_distance
FROM gw.events
ORDER BY common_name;