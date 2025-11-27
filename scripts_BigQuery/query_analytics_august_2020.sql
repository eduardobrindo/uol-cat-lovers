/* Objetivo: Exportar fatos de Agosto de 2020 para o GCS SOMENTE se houver dados.
Solicitante: Time de Analytics.
Estratégia: Usa Tabela Temporária para persistir o resultado antes de exportar.
*/

BEGIN
  DECLARE timestamp_str STRING;
  DECLARE file_uri STRING;
  DECLARE export_query STRING;
  DECLARE row_count INT64;

  -- 1. Cria Tabela Temporária com os dados filtrados
  -- Usamos 'OR REPLACE' para permitir reexecuções na mesma sessão
  CREATE OR REPLACE TEMP TABLE _SESSION.temp_analytics_aug2020 AS
  SELECT 
    fact_id,
    text,
    updated_at
  FROM 
    `dante-causa.analytics.cat_facts`
  WHERE 
    -- Filtro otimizado usando TIMESTAMP_TRUNC para o mês de Agosto de 2020
    TIMESTAMP_TRUNC(updated_at, MONTH) = TIMESTAMP("2020-08-01")
  ORDER BY
    updated_at DESC;

  -- 2. Conta quantas linhas foram capturadas
  SET row_count = (SELECT COUNT(*) FROM _SESSION.temp_analytics_aug2020);

  -- 3. Lógica Condicional: Só exporta se tiver dados
  IF row_count > 0 THEN
    
    -- Prepara o nome do arquivo com timestamp atual (Brasília)
    -- Padrão de nome: cat_facts_analytics_aug2020_YYYYMMDDHHMMSS_*.csv
    SET timestamp_str = FORMAT_DATETIME("%Y%m%d%H%M%S", CURRENT_DATETIME("America/Sao_Paulo"));
    SET file_uri = FORMAT('gs://cat_lovers_analytics/cat_facts_analytics_aug2020_%s_*.csv', timestamp_str);

    -- Monta o comando de exportação dinâmico lendo da tabela temporária
    SET export_query = FORMAT("""
      EXPORT DATA OPTIONS(
        uri='%s',
        format='CSV',
        overwrite=true,
        header=true,
        field_delimiter=','
      ) AS
      SELECT * FROM _SESSION.temp_analytics_aug2020
    """, file_uri);

    -- Executa a exportação
    EXECUTE IMMEDIATE export_query;
    
    -- Retorna mensagem de sucesso com detalhes
    SELECT FORMAT('✅ Sucesso! Arquivo gerado com %d linhas para Analytics em %s', row_count, file_uri) AS resultado;

  ELSE
    -- Se estiver vazio, apenas avisa e não gera arquivo no bucket
    SELECT '⚠️ Nenhum dado encontrado para Agosto de 2020. Arquivo não gerado.' AS resultado;
  END IF;

END;