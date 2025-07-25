# Jinja
## Setting variable
```jinja
{% set my_string = 'hello world' %}
{% set my_int = 1 %}
```

## Looping
```jinja
{% for alphabet in my_list %}

    current alphabet is {{alphabet}}

{% endfor %}
```

## Conditional statement
```jinja
{%  set temp = 45 %}

{% if temp >45 %}
    time for cappucino
{% else %}
    time for soda
{% endif %}
```

## Accessing list
```jinja
{% set my_list = ['a','b']  %}

{{ my_list[0] }}
```

## Accessing dictionary
```jinja
{% set my_dict = 
{
    'nama': 'agus',
    'status': 'hidup'
}  %}

{{ my_dict['nama'] }}
```
# Installing packages
dibuat di packages.yml, lalu run dbt deps

# Macro
fungsi buatan yang dibuat menggunakan jinja.
Ditaruh di dalam folder Macros

## Grant select
```jinja
{% macro snowflake__grant_select(relation, grantees) %}
    {% for grantee in grantees %}
        grant select on {{ relation }} to role {{ grantee }};
    {% endfor %}
{% endmacro %}

```
1. Relation: objek database (tabel, view) yang dibuat oleh model dbt.
2. Grantees: daftar role/user yang akan diberi akses SELECT.

## Union table by prefix
```
{% macro union_tables_by_prefix(database, schema, prefix) %}
    {% set relations = dbt_utils.get_relations_by_prefix(
        schema=schema,
        prefix=prefix,
        database=database
    ) %}

    {% if relations | length == 0 %}
        select null as dummy_column where false
    {% else %}
        {% set sql_parts = [] %}
        {% for rel in relations %}
            {% do sql_parts.append("select * from " ~ rel) %}
        {% endfor %}
        {{ return(sql_parts | join(" union all ")) }}
    {% endif %}
{% endmacro %}

```

## Clean Slate
Membersihkan objek-objek lama di database/schema seperti drop table/view lama agar tidak mengganggu run selanjutnya.

```
{% macro clean_slate(database, schema, prefix) %}
    {% set relations = dbt_utils.get_relations_by_prefix(
        schema=schema,
        prefix=prefix,
        database=database
    ) %}

    {% for relation in relations %}
        drop {{ relation.type }} if exists {{ relation }};
    {% endfor %}
{% endmacro %}

```