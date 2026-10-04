def test_update_display_name_is_not_applied_to_name_column(client, headers, scenario, db):
    """Quirk: SenderAccountUpdate.display_name is setattr'd onto a non-existent column,
    so the stored `name` does not change."""
    r = client.put(f"/sender-accounts/{scenario.sender.id}", json={"display_name": "Renamed"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Sender Name"
