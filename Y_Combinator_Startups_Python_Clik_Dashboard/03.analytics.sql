-- Посмотрим, сколько компаний с разными статусами.
SELECT
    status,
    COUNT() AS companies
FROM yc_companies
GROUP BY status
ORDER BY companies DESC;

-- Сколько компаний купили и сколько вышло на биржу?
SELECT
    COUNTIf(status = 'Acquired') AS acquired,
    COUNTIf(status = 'Public') AS public,
    COUNT() AS total
FROM yc_companies;

-- Рост YC по годам
SELECT
    toUInt16('20' || substring(batch, 2)) AS year,
    COUNT() AS companies
FROM yc_companies
GROUP BY year
ORDER BY year;

-- Из каких индустрий выходят стартапы?
SELECT
    arrayJoin(industries) AS industry,
    COUNT() AS companies
FROM yc_companies
GROUP BY industry
ORDER BY companies DESC
LIMIT 15;

-- На какие темы выстреливали стартапы?
SELECT
    arrayJoin(tags) AS tag,
    COUNT() AS companies
FROM yc_companies
GROUP BY tag
ORDER BY companies DESC
LIMIT 20;

-- Где больше топовых компаний?
SELECT
    arrayJoin(industries) AS industry,
    COUNTIf(has_badge = 1) AS top_companies,
    COUNT() AS total_companies,
    round(countIf(has_badge = 1) * 100.0 / count(), 1) AS top_percent
FROM yc_companies
GROUP BY industry
ORDER BY top_companies DESC
LIMIT 15;

-- Свежий тренд
SELECT
    arrayJoin(tags) AS tag,
    COUNT() AS companies
FROM yc_companies
WHERE toUInt16('20' || substring(batch, 2)) >= 2023
GROUP BY tag
ORDER BY companies DESC
LIMIT 10;