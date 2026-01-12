from brunhilda.parser import parse_description, parse_requirements, parse_steps, parse_tags

# --- Tests parse_steps ---


def test_parse_steps():
    description = """
    @steps
    1) > Connect device
    Continue description of step 1
    > Expect device to be connected
    @endsteps
    """

    test_steps = [{'number': 1, 'result': 'PASS', 'comment': 'OK', 'obtained': 'Device connected'}]

    steps = parse_steps(test_steps, description)

    assert len(steps) == 1
    assert steps[0]['number'] == 1
    assert 'Connect device\nContinue description of step 1' == steps[0]['description']
    assert 'Expect device to be connected' == steps[0]['expectation']

    description = """
    @steps
    1) > | Connect the P1P2 simulator device and add Hydro slave device, then start the initial communication
        | between the simulated Hydro and DUT and wait for the state NORMAL in DUT.
        | Launch the debug GUI tool.
    > | DUT reaches NORMAL state.
        | The launch of the debug GUI tool is successful.
    2) > From debug set [language] to 27 or 28. Read value for item {region_setting} using debug GUI.
    > Value for item {region_setting} is set to 1.
    3) > From debug set [language] to 29 or 30. Read value for item {region_setting} using debug GUI.
    > Value for item {region_setting} is set to 2.
    4) > From debug set [language] to 1. Read value for item {region_setting} using debug GUI.
    > Value for item is set to 0.
    @endsteps
    """

    test_steps = [
        {
            'number': 1,
            'result': 'PASS',
            'comment': 'OK',
            'obtained': ''
        }, {
            'number': 2,
            'result': 'PASS',
            'comment': 'OK',
            'obtained': ''
        }, {
            'number': 3,
            'result': 'PASS',
            'comment': 'OK',
            'obtained': ''
        }, {
            'number': 4,
            'result': 'PASS',
            'comment': 'OK',
            'obtained': ''
        }
    ]

    steps = parse_steps(test_steps, description)

    assert len(steps) == 4

    assert steps[0]['number'] == 1
    assert steps[1]['number'] == 2
    assert steps[2]['number'] == 3
    assert steps[3]['number'] == 4

    assert '| Connect the P1P2 simulator device and add Hydro slave device, then start the initial communication\n| between the simulated Hydro and DUT and wait for the state NORMAL in DUT.\n| Launch the debug GUI tool.' == steps[
        0]['description']
    assert '| DUT reaches NORMAL state.\n| The launch of the debug GUI tool is successful.' == steps[0]['expectation']

    assert 'From debug set [language] to 27 or 28. Read value for item {region_setting} using debug GUI.' == steps[1][
        'description']
    assert 'Value for item {region_setting} is set to 1.' == steps[1]['expectation']

    assert 'From debug set [language] to 29 or 30. Read value for item {region_setting} using debug GUI.' == steps[2][
        'description']
    assert 'Value for item {region_setting} is set to 2.' == steps[2]['expectation']

    assert 'From debug set [language] to 1. Read value for item {region_setting} using debug GUI.' == steps[3][
        'description']
    assert 'Value for item is set to 0.' == steps[3]['expectation']


def test_parse_steps_empty_or_none():
    assert parse_steps([], '') == []
    assert parse_steps([], None) == []

    desc = 'Just description'
    assert parse_steps([], desc) == []

    desc_steps = """
    @steps
    1) > Description
    @endsteps
    """
    steps = parse_steps([], desc_steps)
    assert len(steps) == 1
    assert steps[0]['number'] == 1
    assert steps[0]['description'] == 'Description'
    assert steps[0]['expectation'] == ''


# --- Tests parse_tags ---


def test_parse_tags_basic():
    description = """
    Test login functionality
    @author: John Doe
    @priority High
    @id 12345
    """
    tags = parse_tags(description)

    assert tags['author'] == ['John Doe']
    assert tags['priority'] == ['High']
    assert tags['id'] == ['12345']


def test_parse_tags_lists_and_formatting():
    description = """
    @TAGS smoke, regression, gui;
    @CoMpOnEnT:  Backend
    """
    tags = parse_tags(description)

    assert tags['tags'] == ['smoke', 'regression', 'gui']
    assert tags['component'] == ['Backend']


def test_parse_tags_empty_value():
    description = '@wip'
    tags = parse_tags(description)

    assert tags['wip'] == ['']


def test_parse_tags_ignored():
    description = """
    @steps
    1) > Step
    @endsteps
    """
    tags = parse_tags(description)
    assert tags == {}


def test_parse_tags_none_or_empty():
    assert parse_tags(None) == {}
    assert parse_tags('') == {}
    assert parse_tags(123) == {}


# --- Tests parse_requirements ---


def test_parse_requirements_single():
    description = """
    Some description
    @spec REQ-001
    """
    reqs = parse_requirements(description)
    assert reqs == ['REQ-001']


def test_parse_requirements_multiple():
    description = '@spec: REQ-A, REQ-B,  REQ-C '
    reqs = parse_requirements(description)
    assert reqs == ['REQ-A', 'REQ-B', 'REQ-C']


def test_parse_requirements_first_match_only():
    description = """
    @spec MAIN-REQ
    @spec SECONDARY-REQ
    """
    reqs = parse_requirements(description)
    assert reqs == ['MAIN-REQ']


def test_parse_requirements_none_found():
    description = 'Just description without spec'
    reqs = parse_requirements(description)
    assert reqs == ['-']


def test_parse_requirements_edge_cases():
    assert parse_requirements(None) == ['-']
    assert parse_requirements('') == ['-']


# --- Tests parse_description ---


def test_parse_description_clean():
    description = """
    Title of the test

    @author Me

    Description line 1.
    Description line 2.

    @steps
    1) > Do something
    @endsteps

    Final note.
    """

    clean_desc = parse_description(description)
    lines = clean_desc.splitlines()

    content = [line.strip() for line in lines]

    assert 'Title of the test' in content
    assert 'Description line 1.' in content
    assert 'Description line 2.' in content
    assert 'Final note.' in content

    assert '@author' not in clean_desc
    assert '@steps' not in clean_desc
    assert 'Do something' not in clean_desc


def test_parse_description_no_tags():
    desc = 'Just simple text.'
    assert parse_description(desc) == 'Just simple text.'


def test_parse_description_none():
    assert parse_description(None) == ''
    assert parse_description(123) == ''
