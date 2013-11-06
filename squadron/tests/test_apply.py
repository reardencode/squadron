from .. import main
import pytest
import jsonschema
from helper import are_dir_trees_equal
import os
import shutil

def checkfile(filename, compare):
    with open(filename) as ofile:
        assert compare == ofile.read()

def test_basic():
    node = {'services' : ['api'], 'env' : 'dev'}
    results = main.apply('applytests/applytest1', node)

    assert len(results) == 1
    assert are_dir_trees_equal(results['api']['dir'], 'applytests/applytest1result')

    checkfile('/tmp/test1.out', '55')
    checkfile('/tmp/test2.out', '0')
    os.remove('/tmp/test1.out')
    os.remove('/tmp/test2.out')
    shutil.rmtree(results['api']['dir'])

def test_schema_validation_error():
    node = {'services' : ['api'], 'env' : 'dev'}

    with pytest.raises(jsonschema.ValidationError) as ex:
        main.apply('applytests/applytest1-exception', node)

    assert ex.value.cause is None # make sure it was a validation error
    assert ex.value.validator_value == 'integer'

def test_commit(tmpdir):
    tmpdir = str(tmpdir)
    base_dir = os.path.join(tmpdir, 'base_dir')
    serv_dir = os.path.join(tmpdir, 'serv_dir')
    atom_yes = 'atomic'
    atom_no = 'atomic-no'
    atom_dir = os.path.join(serv_dir, atom_yes)
    atom_no_dir = os.path.join(serv_dir, atom_no)

    dir_info = {'api': {'base_dir' : base_dir, 'dir' : serv_dir,
        'atomic': {atom_yes : True, atom_no : False}}}

    # Atomic file
    os.makedirs(atom_dir)
    with open(os.path.join(atom_dir, 'atom.txt'), 'w') as wfile:
        wfile.write('atomic update')

    # Non-atomic directory
    os.makedirs(atom_no_dir)
    with open(os.path.join(atom_no_dir, 'atom-no.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    # Non-atomic file
    with open(os.path.join(serv_dir, 'non-atom.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    main.commit(dir_info)

    assert are_dir_trees_equal(base_dir, serv_dir)

    assert os.path.islink(os.path.join(base_dir, atom_yes)) == True
    assert os.path.islink(os.path.join(base_dir, atom_no)) == False

