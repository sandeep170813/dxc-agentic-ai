from triage import triage


def test_ac1_sixty_affected_users_is_p1_with_sla_4():
    result = triage({"title": "Any issue", "description": "", "affected_users": 60})
    assert result == {"priority": "P1", "queue": "General", "sla_hours": 4}


def test_ac2_email_outage_is_p1():
    result = triage({"title": "Email outage", "description": "", "affected_users": 1})
    assert result["priority"] == "P1"


def test_ac3_download_does_not_match_down():
    result = triage({"title": "Slow download speed", "description": "", "affected_users": 1})
    assert result["priority"] == "P4"


def test_ac4_twelve_users_is_p2_with_sla_8():
    result = triage({"title": "Any issue", "description": "", "affected_users": 12})
    assert result == {"priority": "P2", "queue": "General", "sla_hours": 8}


def test_ac5_urgent_cannot_print_is_p2():
    result = triage({"title": "URGENT: cannot print", "description": "", "affected_users": 1})
    assert result["priority"] == "P2"


def test_ac6_three_users_is_p3_with_sla_24():
    result = triage({"title": "Any issue", "description": "", "affected_users": 3})
    assert result == {"priority": "P3", "queue": "General", "sla_hours": 24}


def test_ac7_laptop_wifi_broken_goes_to_network():
    result = triage({"title": "Laptop wifi broken", "description": "", "affected_users": 1})
    assert result["queue"] == "Network"


def test_ac8_password_reset_goes_to_access():
    result = triage({"title": "Password reset", "description": "", "affected_users": 1})
    assert result["queue"] == "Access"


def test_ac9_empty_title_and_zero_users_raise_value_error():
    try:
        triage({"title": "", "description": "", "affected_users": 1})
        assert False, "expected ValueError for empty title"
    except ValueError:
        pass

    try:
        triage({"title": "Any issue", "description": "", "affected_users": 0})
        assert False, "expected ValueError for zero users"
    except ValueError:
        pass