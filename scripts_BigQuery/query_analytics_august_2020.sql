/* Objetivo: Extrair fatos atualizados em Agosto de 2020.
Solicitante: Time de Analytics.
*/

SELECT 
  fact_id,
  text,
  updated_at
FROM 
  `dante-causa.analytics.cat_facts`
WHERE 
  TIMESTAMP_TRUNC(updated_at, MONTH) = TIMESTAMP("2020-08-01")
ORDER BY
  updated_at DESC;