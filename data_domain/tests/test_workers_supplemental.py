import os

import pytest

from backstop_dd.workers import supplemental, tables
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


@pytest.mark.skip("Currently not working - supplemental_out is list, but needs .items")
def test_get_financial_supplemental_details(mock_db):
    # TODO supplemental.get_financial_supplemental_details takes in supplemental_out
    # get_financial_supplemental_details expects it to have ".items" attributre
    # AttributeError: 'list' object has no attribute 'items'
    with mock_db.connect(host=db_host, port=db_port) as conn:
        query_supplemental = (
            RethinkDB().db("Backstop").table(tables.supplemental).run(conn)[:3]
        )

    for query in query_supplemental:

        ptf = query["PTF"]
        supplemental_out = (
            RethinkDB()
            .db("Backstop")
            .table(tables.supplemental)
            .filter({"PTF": ptf})
            .run(conn)
        )

        # test the function
        supp_dict = supplemental.get_financial_supplemental_details(supplemental_out)

        assert isinstance(supp_dict, dict)
        assert isinstance(supp_dict["total_budget"], float)
        assert isinstance(supp_dict["total_expense"], float)
