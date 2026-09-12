-- Invantive Query Tool / Data Hub
-- Extract an Excel sheet into Supabase (PostgreSQL alias @pg).
--
-- Map columns by position (1 = first column of the range/sheet).
-- Change the file path, worksheet, and column list to match your workbook.
-- Test in Query Tool, then schedule with Data Hub.

local on error continue

-- One named range (preferred: data-only, no titles).
create or replace table excel_sales_estimates@pg
as
select sysdateutc as loaded_at
,      xlsx.*
from   exceltable
       ( name 'salesdata'
         passing file 'C:\data\sales.xlsx'
         skip empty rows
         columns region       varchar2 position 1
         ,       item_code    varchar2 position next
         ,       sales_period number   position next
         ,       revenue      number   position next
       ) xlsx
;

-- Alternative: first worksheet, skip header row.
-- create or replace table excel_sales_estimates@pg
-- as
-- select sysdateutc as loaded_at
-- ,      xlsx.*
-- from   exceltable
--        ( worksheet 1
--          passing file 'C:\data\sales.xlsx'
--          skip first 1 rows
--          skip empty rows
--          columns region       varchar2 position 1
--          ,       item_code    varchar2 position next
--          ,       sales_period number   position next
--          ,       revenue      number   position next
--        ) xlsx
-- ;

-- Folder of workbooks (Dropbox / OneDrive sync folder on this machine).
-- create or replace table excel_sales_estimates@pg
-- as
-- select fle.file_path
-- ,      sysdateutc as loaded_at
-- ,      xlsx.*
-- from   files('C:\data\drop', '*.xlsx', false)@os fle
-- join   exceltable
--        ( worksheet 1
--          passing file fle.file_path
--          skip first 1 rows
--          skip empty rows
--          columns region    varchar2 position 1
--          ,       item_code varchar2 position next
--          ,       revenue   number   position next
--        ) xlsx
-- ;
