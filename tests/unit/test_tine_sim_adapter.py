
from adapter.petra.TineSimAdapter import PetraSimDatabase


class DBConnectorMock:
    def check_if_sql_db_table_exists(self, tablename):
        return True

    def wait_until_table_is_created(self, table: str):
        pass


def petra_db_create_update_queries():
    db = PetraSimDatabase(sql_connector=DBConnectorMock())
    queries = db._create_update_queries(
        "table", "params", [[["params", "test"], ["value", 1]], [["params", "test1"], ["value", 2]]]
    )
    print(queries)

    assert queries[0] == "Update table set value=1 where params='test'" and queries[1] == "Update table set value=2 where params='test1'"


def test_simulation_petra_db_query_2():
    db = PetraSimDatabase(sql_connector=DBConnectorMock())
    queries = db._create_update_queries(
        "table", "params", [[["params", "test"], ["value", 1], ['name', 'test_name']], [["params", "test1"], ["value", 2], ['name', 'test_name1']]]
    )
    print(queries)

    assert queries[0] == "Update table set value=1,name='test_name' where params='test'" and queries[1] == "Update table set value=2,name='test_name1' where params='test1'"
