from acfo.sqlsplit import split_sql


def test_split_respects_dollar_quotes():
    script = """
    create table t (id int);
    insert into work_orders (body) values (
    $wo$Phase 2; not a split.
    more;$wo$
    );
    """
    statements = split_sql(script)
    assert len(statements) == 2
    assert "Phase 2; not a split." in statements[1]
