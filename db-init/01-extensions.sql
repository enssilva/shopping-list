CREATE EXTENSION IF NOT EXISTS unaccent;

-- Criar uma versão imutável da função unaccent para poder usar em índices
CREATE OR REPLACE FUNCTION unaccent_immutable(text)
  RETURNS text AS
$func$
  SELECT public.unaccent('public.unaccent', $1);
$func$ LANGUAGE sql IMMUTABLE;