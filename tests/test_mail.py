
import pytest
import backup.mail as mail


def test_week_nr_in_report():
    stats = []
    assert 'week 1' in mail.generate_report(stats, 1)
    assert 'week 5' in mail.generate_report(stats, 5)


def test_report_generation_includes_all_servers():
    stats = [MockServerStats('server1'), MockServerStats('server2')]
    report = mail.generate_report(stats, 1)
    assert stats[0].server_name in report
    assert stats[1].server_name in report


@pytest.mark.xfail(reason='Not implemented yet, requires "real" server stats.')
def test_report_generation():
    pass


# Helper mocks:

class MockServerStats(object):

    def __init__(self, server_name):
        self.server_name = server_name

    @property
    def report(self):
        return f'- Server: {self.server_name}'
