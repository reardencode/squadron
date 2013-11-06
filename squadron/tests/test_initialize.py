from .. import initialize
import os

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    initialize.init(tmpdir, True, None, force=True)

    items = os.listdir(tmpdir)
    assert len(items) > 0

def test_service(tmpdir):
    tmpdir = str(tmpdir)
    initialize.initService(tmpdir, 'api')

    items = os.listdir(os.path.join(tmpdir, 'api'))

    assert len(items) > 0