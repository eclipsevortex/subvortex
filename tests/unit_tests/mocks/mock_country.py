def mock_get_country(mock_get_country, axon_details):
    def side_effect(*args):
        subregion, country = next(((x["subregion"], x["country"]) for x in axon_details if x["ip"] == args[0]), None)
        return (subregion, country) or ("Northern Europe", "GB")

    mock_get_country.side_effect = side_effect
