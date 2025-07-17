USE `database`;

WITH RECURSIVE date_split AS (
  SELECT 
    apartment_id,
    room_id,
    user_id,
    start_date AS split_start,
    LEAST(LAST_DAY(start_date), end_date) AS split_end,
    start_date,
    end_date
  FROM booking_apartment

  UNION ALL

  SELECT 
    apartment_id,
    room_id,
    user_id,
    DATE_ADD(split_end, INTERVAL 1 DAY),
    LEAST(LAST_DAY(DATE_ADD(split_end, INTERVAL 1 DAY)), end_date),
    start_date,
    end_date
  FROM date_split
  WHERE split_end < end_date
),

room_occupancy AS (
  SELECT 
    apartment_id, 
    room_id,
    SUM(DATEDIFF(split_end, split_start) + 1)/30 AS occupancy_rate,
    MONTH(split_end) AS month
  FROM date_split
  GROUP BY apartment_id, room_id, MONTH(split_end)
)

SELECT 
  apartment_id,
  month,
  AVG(occupancy_rate) AS avg_occupancy_rate
FROM room_occupancy
GROUP BY apartment_id, month
ORDER BY apartment_id, month;
