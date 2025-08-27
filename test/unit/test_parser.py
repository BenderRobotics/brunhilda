from brunhilda.parser import parse_steps


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
