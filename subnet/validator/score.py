import bittensor as bt
from typing import List
from collections import Counter

from subnet.validator.models import Miner
from subnet.validator.bonding import wilson_score_interval
from subnet.validator.constants import CHALLENGE_NAME
from subnet.constants import (
    AVAILABILITY_FAILURE_REWARD,
    RELIABILLITY_FAILURE_REWARD,
    LATENCY_FAILURE_REWARD,
    PERFORMANCE_FAILURE_REWARD,
    DISTRIBUTION_FAILURE_REWARD,
    AVAILABILITY_WEIGHT,
    LATENCY_WEIGHT,
    PERFORMANCE_WEIGHT,
    RELIABILLITY_WEIGHT,
    DISTRIBUTION_WEIGHT,
)

# Longest distance between any two places on Earth is 20,010 kilometers
MAX_DISTANCE = 20010

INDIVIDUAL_WEIGHT = 0.6
TEAM_WEIGHT = 0.4


def check_multiple_miners_on_same_ip(miner: Miner, miners: List[Miner]):
    """
    Check if there is more than one miner per ip
    """
    count = sum(1 for item in miners if item.ip == miner.ip)
    if count > 1:
        bt.logging.warning(
            f"[{miner.uid}][Score][Multiple Ip] {count} miner(s) associated with the ip"
        )

    return count


def can_compute_availability_score(miner: Miner):
    """
    True if we can compute the availaiblity score, false to get the penalty
    """
    return miner.verified and not miner.has_ip_conflicts


def compute_availability_score(miner: Miner):
    """
    Compute the availability score of the uid
    """

    score = (
        1.0 if can_compute_availability_score(miner) else AVAILABILITY_FAILURE_REWARD
    )

    return score


def can_compute_reliability_score(miner: Miner):
    """
    True if we can compute the reliability score, false to get the penalty
    """
    return True


async def compute_reliability_score(miner: Miner):
    """
    Compute the reliaiblity score of the uid based on the the ratio challenge_successes/challenge_attempts
    """
    if not can_compute_reliability_score(miner):
        return RELIABILLITY_FAILURE_REWARD

    # Step 1: Retrieve statistics
    is_successful = miner.verified and not miner.has_ip_conflicts
    miner.challenge_successes = miner.challenge_successes + int(is_successful)
    miner.challenge_attempts = miner.challenge_attempts + 1
    bt.logging.trace(
        f"[{miner.uid}][Score][Reliability] # challenge attempts {miner.challenge_attempts}"
    )
    bt.logging.trace(
        f"[{miner.uid}][Score][Reliability] # challenge succeeded {miner.challenge_successes}"
    )

    # Step 2: Normalization
    score = wilson_score_interval(miner.challenge_successes, miner.challenge_attempts)

    return score


def can_compute_latency_score(miner: Miner):
    """
    True if we can compute the latency score, false to get the penalty
    """
    return miner.verified and not miner.has_ip_conflicts


def compute_latency_score(miner: Miner, miners: List[Miner]):
    """
    Compute the latency score of the uid based on the process time of all uids
    """
    if not can_compute_latency_score(miner):
        return LATENCY_FAILURE_REWARD

    subregion = miner.subregion
    countries = [x.country for x in miners if miner.subregion == subregion]

    # Compute score based on miner routing time against other in the same country
    routing_times = [x.routing_time for x in miners if x.country == miner.country]
    min_time = min(routing_times)
    max_time = max(routing_times)
    first_score = (
        1.0
        if max_time - min_time == 0
        else (max_time - miner.routing_time) / (max_time - min_time)
    )
    bt.logging.trace(
        f"[{miner.uid}] First score {first_score} ({miner.routing_time}) [{min_time}, {max_time}]"
    )

    # Compute score based on number of miner in the miner's country again other country in the same subregion
    subregion_miners = [x for x in miners if miner.country in countries]
    counters = Counter(x.country for x in subregion_miners)
    min_count = min(counters.values())
    max_count = max(counters.values())
    count = counters[miner.country]
    second_score = (
        1.0
        if max_count - min_count == 0
        else (count - min_count) / (max_count - min_count)
    )
    bt.logging.trace(
        f"[{miner.uid}] Second score {second_score} ({count}) [{min_count}, {max_count}]"
    )

    # Compute score based on average routing time in miner's country against other country in the same subregion
    avg_routing_times = [
        sum(t) / len(t)
        for country in countries
        if (t := [x.routing_time for x in miners if x.country == country])
    ]
    min_time = min(avg_routing_times)
    max_time = max(avg_routing_times)
    avg_routing_time = avg_routing_times[countries.index(miner.country)]
    third_score = (
        1.0
        if max_time - min_time == 0
        else (max_time - avg_routing_time) / (max_time - min_time)
    )
    bt.logging.trace(
        f"[{miner.uid}] Third score {third_score} ({avg_routing_time}) [{min_time}, {max_time}]"
    )

    # Compute score based on number of miner in the miner subregion again other subregion in the world
    counters = Counter(x.subregion for x in miners)
    min_count = min(counters.values())
    max_count = max(counters.values())
    count = counters[miner.subregion]
    fourth_score = (
        1.0
        if max_count - min_count == 0
        else (count - min_count) / (max_count - min_count)
    )
    bt.logging.trace(
        f"[{miner.uid}] Fourth score {fourth_score} ({count}) [{min_count}, {max_count}]"
    )

    return (((first_score + second_score) / 2) * INDIVIDUAL_WEIGHT) + (
        ((third_score + fourth_score) / 2) * TEAM_WEIGHT
    )


def can_compute_performance_score(miner: Miner):
    """
    True if we can compute the performance score, false to get the penalty
    """
    return miner.verified and not miner.has_ip_conflicts


def compute_performance_score(miner: Miner, miners: List[Miner]):
    """
    Compute the performance score of the uid based on the process time of all uids
    """
    if not can_compute_performance_score(miner):
        return PERFORMANCE_FAILURE_REWARD

    process_time = miner.process_time
    bt.logging.trace(f"[{miner.uid}][Score][Performance] Process time {process_time}")

    # Step 1: Get the process times of the miners
    process_times = [miner.process_time for miner in miners]

    # Step 2: Normalization
    min_time = min(process_times)
    bt.logging.trace(
        f"[{miner.uid}][Score][Performance] Minimum process time {min_time}"
    )
    max_time = max(process_times)
    bt.logging.trace(
        f"[{miner.uid}][Score][Performance] Maximum process time {max_time}"
    )

    if max_time == min_time == process_time:
        # Only one uid with process time
        return 1

    score = (max_time - process_time) / (max_time - min_time)

    return score


def can_compute_distribution_score(miner: Miner):
    """
    True if we can compute the distribution score, false to get the penalty
    """
    return miner.verified and not miner.has_ip_conflicts


def compute_distribution_score(miner: Miner, miners: List[Miner]):
    """
    Compute the distribution score of the uid based on the country of all uids
    """
    if not can_compute_distribution_score(miner):
        return DISTRIBUTION_FAILURE_REWARD

    # Step 1: Country of the requested response
    country = miner.country

    # Step 2; Exclude miners not verified or with ip conflicts
    conform_miners = [
        miner for miner in miners if miner.verified and not miner.has_ip_conflicts
    ]

    # Step 3: Country the number of miners in the country
    count = 0
    for item in conform_miners:
        if item.country == country:
            count = count + 1
    bt.logging.trace(f"[{miner.uid}][Score][Distribution] {count} uids in {country}")

    # Step 4: Compute the score
    score = 1 / count if count > 0 else 0

    return score


def compute_final_score(miner: Miner):
    """
    Compute the final score based on the different scores (availability, reliability, latency and distribution)
    """
    # Use a smaller weight if the subtensor is available but desync (miner block < validator block - 1)
    availability_weight = (
        3 if miner.verified and not miner.sync else AVAILABILITY_WEIGHT
    )

    numerator = (
        (availability_weight * miner.availability_score)
        + (LATENCY_WEIGHT * miner.latency_score)
        + (PERFORMANCE_WEIGHT * miner.performance_score)
        + (RELIABILLITY_WEIGHT * miner.reliability_score)
        + (DISTRIBUTION_WEIGHT * miner.distribution_score)
    )

    denominator = (
        availability_weight
        + LATENCY_WEIGHT
        + PERFORMANCE_WEIGHT
        + RELIABILLITY_WEIGHT
        + DISTRIBUTION_WEIGHT
    )

    score = numerator / denominator if denominator != 0 else 0

    if miner.suspicious:
        penalty_factor = miner.penalty_factor or 0
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Applying penalty factor of {penalty_factor}"
        )
        score = penalty_factor * score

    return score
