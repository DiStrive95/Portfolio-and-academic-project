-- Просмотр всех событий
SELECT
    common_name,
    mass_1_source,
    mass_2_source,
    total_mass_source,
    luminosity_distance,
    merger_type
FROM gw.events
ORDER BY total_mass_source DESC;

-- Сколько событий на каждый тип слияния?(Зафиксировано всего одно слияние нейтронных звёзд)
SELECT
    merger_type,
    COUNT() AS events
FROM gw.events
GROUP BY merger_type
ORDER BY events DESC;

-- Топ-3 по общей массе
SELECT
    common_name,
    total_mass_source,
    luminosity_distance
FROM gw.events
ORDER BY total_mass_source DESC
LIMIT 3;

-- Топ-3 по расстоянию от нас
SELECT
    common_name,
    luminosity_distance,
    total_mass_source
FROM gw.events
ORDER BY luminosity_distance DESC
LIMIT 3;

-- Связь массы и расстояния.(При большой массе объектов, расстояние до гравитациоонного события растёт.
-- У единственного слияния нейтронных звёзд самое короткое расстояние до нас. Получается, такой вид слияния
-- фиксируется радарами только при относительно близком расстоянии к нам)
SELECT
    merger_type,
    COUNT() AS events,
    ROUND(AVG(total_mass_source), 1) AS avg_mass,
    ROUND(AVG(luminosity_distance), 0) AS avg_distance,
    ROUND(AVG(network_snr), 1) AS avg_snr
FROM gw.events
GROUP BY merger_type
ORDER BY avg_mass DESC;

-- В 2017 году это событие доказало, что гравитационные волны идут со скоростью света.
SELECT *
FROM gw.events
WHERE common_name = 'GW170817';