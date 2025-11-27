/* Objetivo: Exportar amostra QA para o GCS SOMENTE se houver dados.
   Estratégia: Usa Tabela Temporária para persistir a amostra antes de exportar.
*/

BEGIN
  DECLARE timestamp_str STRING;
  DECLARE file_uri STRING;
  DECLARE export_query STRING;
  DECLARE row_count INT64;

  -- 1. Cria uma Tabela Temporária com a amostra
  -- Usamos 'OR REPLACE' para não dar erro se rodar várias vezes na mesma sessão
  CREATE OR REPLACE TEMP TABLE _SESSION.temp_qa_sample AS
  SELECT 
    text,
    updated_at
  FROM 
    `dante-causa.analytics.cat_facts`
  WHERE 
    RAND() < 0.1;

  -- 2. Conta quantas linhas foram capturadas
  SET row_count = (SELECT COUNT(*) FROM _SESSION.temp_qa_sample);

  -- 3. Lógica Condicional: Só exporta se tiver dados
  IF row_count > 0 THEN
    
    -- Prepara o nome do arquivo
    SET timestamp_str = FORMAT_DATETIME("%Y%m%d%H%M%S", CURRENT_DATETIME("America/Sao_Paulo"));
    SET file_uri = FORMAT('gs://cat_lovers_analytics/cat_facts_qa_sample_%s_*.csv', timestamp_str);

    -- Monta o comando de exportação lendo da tabela temporária
    SET export_query = FORMAT("""
      EXPORT DATA OPTIONS(
        uri='%s',
        format='CSV',
        overwrite=true,
        header=true,
        field_delimiter=','
      ) AS
      SELECT * FROM _SESSION.temp_qa_sample
    """, file_uri);

    -- Executa a exportação
    EXECUTE IMMEDIATE export_query;
    
    -- Mostra mensagem de sucesso no resultado
    SELECT FORMAT('✅ Sucesso! Arquivo gerado com %d linhas em %s', row_count, file_uri) AS resultado;

  ELSE
    -- Se estiver vazio, apenas avisa e não gera arquivo
    SELECT '⚠️ Amostra vazia (0 linhas sorteadas). Nenhum arquivo foi gerado no Bucket.' AS resultado;
  END IF;

END;