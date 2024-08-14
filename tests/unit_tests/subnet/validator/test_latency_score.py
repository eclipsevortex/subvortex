import unittest
import tests.unit_tests.mocks.mock_miners as mocks

from subnet.validator.score import compute_latency_score, INDIVIDUAL_WEIGHT, TEAM_WEIGHT


def compute_score(first, second, third, fourth):
    return (((first + second) / 2) * INDIVIDUAL_WEIGHT) + (
        ((third + fourth) / 2) * TEAM_WEIGHT
    )


def test_a_not_verified_miner_should_return_a_score_of_zero():
    # Arrange
    miner = mocks.miner_not_verified_1

    # Act
    result = compute_latency_score(miner, [miner])

    # Assert
    assert 0.0 == result


def test_an_ip_conflicts_miner_should_return_a_score_of_zero():
    # Arrange
    miner = mocks.miner_with_ip_conflicts_1

    # Act
    result = compute_latency_score(miner, [miner])

    # Assert
    assert 0.0 == result


def test_a_not_verified_and_ip_conflicts_miner_should_return_a_score_of_zero():
    # Arrange
    miner = mocks.miner_not_verified_and_ip_conflicts_1

    # Act
    result = compute_latency_score(miner, [miner])

    # Assert
    assert 0.0 == result


def test_a_verified_miner_when_alone_should_return_a_score_of_one():
    # Arrange
    miner = mocks.miner_verified

    # Act
    result = compute_latency_score(miner, [miner])

    # Assert
    assert 1.0 == result


def test_a_verified_miner_when_other_miners_are_not_verified_should_return_a_score_of_one():
    # Arrange
    miner = mocks.miner_verified

    miners = [
        miner,
        mocks.miner_not_verified_and_ip_conflicts_1,
        mocks.miner_not_verified_and_ip_conflicts_2,
    ]

    # Act
    result = compute_latency_score(miner, miners)

    # Assert
    assert 1.0 == result


def test_a_verified_miner_when_other_miners_have_ip_conflicts_should_return_a_score_of_one():
    # Arrange
    miner = mocks.miner_verified

    miners = [miner, mocks.miner_with_ip_conflicts_1, mocks.miner_with_ip_conflicts_2]

    # Act
    result = compute_latency_score(miner, miners)

    # Assert
    assert 1.0 == result


def test_a_verified_miner_when_other_miners_are_not_verified_and_have_ip_conflicts_should_return_a_score_of_one():
    # Arrange
    miner = mocks.miner_verified

    miners = [miner, mocks.miner_with_ip_conflicts_1, mocks.miner_with_ip_conflicts_2]

    # Act
    result = compute_latency_score(miner, miners)

    # Assert
    assert 1.0 == result


class TestMinersInACountryWithNoOtherCountryInTheWorldCase(unittest.TestCase):
    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(1, 1, 1, 1)
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(0, 1, 1, 1)
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(0.5, 1, 1, 1)
        assert expected_value == result


class TestWorseCountryInASubregionContainingOtherCountryWithNoOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0, 0, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_in_between_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestMiddleCountryInASubregionContainingOtherCountryWithNoOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.5, 0.19662921348314588, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestBestCountryInASubregionContainingOtherCountryWithNoOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [1, 1, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestWorseCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0, 0, 0]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_fr_with_in_between_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestMiddleCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.2, 0.1037037037037036, 0]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_nl_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestBestCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.4, 0.5274074074074073, 0]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_de_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestWorseCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0, 0.345679012345679, 0.25]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ie_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ie_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ie_with_in_between_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.75, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestBestCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.6, 0.8592592592592593, 0.25]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gb_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gb_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gb_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.875, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestMiddleCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.2, 0.45185185185185184, 0.25]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_no_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_no_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_no_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.5, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestWorseCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.2, 0.5111111111111112, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gl_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gl_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_gl_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.6666666666666666, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestBestCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [1, 1, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_us_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_us_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_us_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.8888888888888888, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


class TestMiddleCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase(
    unittest.TestCase
):
    scores = [0.2, 0.7333333333333334, 1]

    def test_best_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ca_with_best_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            1, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_worse_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ca_with_worst_latency
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result

    def test_middle_miner_when_evaluating_should_return_a_score_between_zero_and_one(
        self,
    ):
        # Arrange
        miner = mocks.miner_ca_with_in_between_latency_1
        miners = [
            mocks.miner_de_with_best_latency,
            mocks.miner_de_with_in_between_latency_1,
            mocks.miner_de_with_in_between_latency_2,
            mocks.miner_de_with_in_between_latency_3,
            mocks.miner_de_with_worst_latency,
            mocks.miner_fr_with_best_latency,
            mocks.miner_fr_with_in_between_latency,
            mocks.miner_fr_with_worst_latency,
            mocks.miner_nl_with_best_latency,
            mocks.miner_nl_with_in_between_latency_1,
            mocks.miner_nl_with_in_between_latency_2,
            mocks.miner_nl_with_worst_latency,
            mocks.miner_us_with_best_latency,
            mocks.miner_us_with_in_between_latency_1,
            mocks.miner_us_with_in_between_latency_2,
            mocks.miner_us_with_in_between_latency_3,
            mocks.miner_us_with_in_between_latency_4,
            mocks.miner_us_with_in_between_latency_5,
            mocks.miner_us_with_in_between_latency_6,
            mocks.miner_us_with_worst_latency,
            mocks.miner_ca_with_best_latency,
            mocks.miner_ca_with_in_between_latency_1,
            mocks.miner_ca_with_in_between_latency_2,
            mocks.miner_ca_with_worst_latency,
            mocks.miner_gl_with_best_latency,
            mocks.miner_gl_with_in_between_latency_1,
            mocks.miner_gl_with_in_between_latency_2,
            mocks.miner_gl_with_worst_latency,
            mocks.miner_gb_with_best_latency,
            mocks.miner_gb_with_in_between_latency_1,
            mocks.miner_gb_with_in_between_latency_2,
            mocks.miner_gb_with_in_between_latency_3,
            mocks.miner_gb_with_in_between_latency_4,
            mocks.miner_gb_with_worst_latency,
            mocks.miner_no_with_best_latency,
            mocks.miner_no_with_in_between_latency_1,
            mocks.miner_no_with_in_between_latency_2,
            mocks.miner_no_with_worst_latency,
            mocks.miner_ie_with_best_latency,
            mocks.miner_ie_with_in_between_latency,
            mocks.miner_ie_with_worst_latency,
        ]

        # Act
        result = compute_latency_score(miner, miners)

        # Assert
        expected_value = compute_score(
            0.75, self.scores[0], self.scores[1], self.scores[2]
        )
        assert expected_value == result


def test_check_the_scores_for_each_testcase():
    # Check for Worse Subregion
    assert (
        sum(
            TestWorseCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestMiddleCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestBestCountryInWorseSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
    )

    # Check for Middle Subregion
    assert (
        sum(
            TestWorseCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestMiddleCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestBestCountryInMiddleSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
    )

    # Check for Best Subregion
    assert (
        sum(
            TestWorseCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestMiddleCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
        < sum(
            TestBestCountryInBestSubregionContainingOtherCountryWithOtherSubregionsInTheWorldCase.scores
        )
    )
