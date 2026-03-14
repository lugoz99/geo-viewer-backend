-- init-postgis.sql
-- Este script se ejecuta cuando la base de datos se inicializa por primera vez

-- Habilitar extensiones necesarias (postgis_tiger_geocoder NO se instala)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
-- CREATE EXTENSION IF NOT EXISTS postgis_raster; -- Descomenta si necesitas raster

-- Opcional: deshabilitar Tiger Geocoder si por alguna razón se intenta instalar
DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE;