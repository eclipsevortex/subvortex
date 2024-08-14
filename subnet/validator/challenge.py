import torch
import time
import random
import asyncio
import subprocess
import bittensor as bt

from subnet.constants import DEFAULT_PROCESS_TIME
from subnet.validator.models import Miner
from subnet.validator.synapse import send_scope
from subnet.validator.security import is_miner_suspicious
from subnet.validator.utils import (
    get_next_uids,
    deregister_suspicious_uid,
)
from subnet.validator.bonding import update_statistics
from subnet.validator.state import log_event
from subnet.validator.score import (
    compute_availability_score,
    compute_reliability_score,
    compute_latency_score,
    compute_performance_score,
    compute_distribution_score,
    compute_final_score,
)
from subnet.validator.constants import CHALLENGE_NAME

MINER_PROPERTIES = [
    "hotkey",
    "coldkey",
    "rank",
    "emission",
    "incentive",
    "consensus",
    "trust",
    "last_update",
    "axon_info",
]

VALIDATOR_PROPERTIES = [
    "hotkey",
    "coldkey",
    "stake",
    "rank",
    "emission",
    "validator_trust",
    "dividends",
    "last_update",
    "axon_info",
]


def create_subtensor_challenge(subtensor: bt.subtensor):
    """
    Create the challenge that the miner subtensor will have to execute
    """
    try:
        # Get the current block from the miner subtensor
        current_block = subtensor.get_current_block()

        # Select a block
        block = random.randint(current_block - 256)

        # Select the subnet
        subnet_count = max(subtensor.get_subnets(block=block))
        subnet_uid = random.randint(0, subnet_count)

        # Select the neuron
        neurons = subtensor.neurons_lite(block=block, netuid=subnet_uid)
        neuron_index = random.randint(0, len(neurons) - 1)
        neuron = neurons[neuron_index]
        neuron_uid = neuron.uid

        # Select the property
        properties = (
            MINER_PROPERTIES if neuron.axon_info.is_serving else VALIDATOR_PROPERTIES
        )
        property_index = random.randint(0, len(properties) - 1)
        neuron_property = properties[property_index]

        # Get the property value
        neuron_value = getattr(neuron, neuron_property)

        return (block, subnet_uid, neuron_uid, neuron_property, neuron_value)
    except Exception as err:
        bt.logging.error(err)
        return None


def challenge_miner(ip: str):
    """
    Challenge the miner by pinging it
    """
    verified = False
    reason = None
    process_time = None
    try:
        # Start the timer
        start_time = time.time()

        # Ping the miner
        output = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Compute the process time
        process_time = time.time() - start_time

        if output.returncode == 0:
            verified = True
        else:
            error_output = output.stderr.decode()
            if "Name or service not known" in error_output:
                reason = "Hostname could not be resolved."
            elif "Destination Host Unreachable" in error_output:
                reason = "Destination host is unreachable."
            elif "Request timeout" in error_output:
                reason = "Request timed out."
            else:
                reason = "Unknown error occurred."
    except Exception as err:
        reason = f"An unexpected error occurred: {str(err)}"

    return (verified, reason, process_time)


def challenge_subtensor(ip: str, challenge):
    """
    Challenge the subtensor by requesting the value of a property of a specific neuron in a specific subnet at a certain block
    """
    verified = False
    reason = None
    process_time = None

    try:
        # Get the details of the challenge
        block, netuid, uid, neuron_property, expected_value = challenge

        # Attempt to connect to the subtensor
        try:
            subtensor = bt.subtensor(network=f"ws://{ip}:9944")
        except Exception:
            reason = "Failed to connect to Subtensor node at the given IP."
            return (verified, reason, process_time)

        # Start the timer
        start_time = time.time()

        # Execute the challenge
        try:
            miner = subtensor.neuron_for_uid_lite(netuid=netuid, uid=uid, block=block)
        except KeyError:
            reason = "Invalid netuid or uid provided."
            return (verified, reason, process_time)
        except ValueError:
            reason = "Invalid or unavailable block number."
            return (verified, reason, process_time)
        except Exception:
            reason = "Failed to retrieve neuron details."
            return (verified, reason, process_time)

        # Access the specified property
        try:
            miner_value = getattr(miner, neuron_property)
        except AttributeError:
            reason = "Property not found in the neuron."
            return (verified, reason, process_time)

        # Compute the process time
        process_time = time.time() - start_time

        # Verify the challenge
        verified = expected_value == miner_value
    except Exception as err:
        reason = f"An unexpected error occurred: {str(err)}"

    return (verified, reason, process_time)


async def handle_challenge(self, uid: int, challenge):
    # Get the miner
    miner: Miner = next((miner for miner in self.miners if miner.uid == uid), None)

    # Set the process time by default
    miner_time: float = DEFAULT_PROCESS_TIME
    process_time: float = DEFAULT_PROCESS_TIME

    # Challenge Miner - Ping time
    miner_verified, miner_reason, miner_time = challenge_miner(miner.ip)

    if miner_verified:
        # Challenge Subtensor - Process time + check the challenge
        subtensor_verified, subtensor_reason, subtensor_time = challenge_subtensor(
            miner.ip, challenge
        )
        process_time = subtensor_time - miner_time

    miner.verified = miner_verified and subtensor_verified
    miner.routing_time = (
        miner_time
        if miner.routing_time != -1
        else (miner.routing_time + miner_time) / 2
    )
    miner.process_time = (
        process_time
        if miner.process_time != -1
        else (miner.process_time + process_time) / 2
    )

    return miner_reason if not miner_verified else subtensor_reason


async def challenge_data(self):
    start_time = time.time()
    bt.logging.debug(f"[{CHALLENGE_NAME}] Step starting")

    # Create the challenge
    challenge = create_subtensor_challenge(self.subtensor)
    if not challenge:
        bt.logging.warning("Failed to create the challenge.")
        return

    # Select the miners
    val_hotkey = self.metagraph.hotkeys[self.uid]
    uids = await get_next_uids(self, val_hotkey)
    bt.logging.debug(f"[{CHALLENGE_NAME}] Available uids {uids}")

    # Get the misbehavior miners
    suspicious_uids = self.monitor.get_suspicious_uids()
    bt.logging.debug(f"[{CHALLENGE_NAME}] Suspicious uids {suspicious_uids}")

    # Execute the challenges
    tasks = []
    reasons = []
    for uid in uids:
        tasks.append(asyncio.create_task(handle_challenge(self, uid, challenge)))
        reasons = await asyncio.gather(*tasks)

    # Initialise the rewards object
    rewards: torch.FloatTensor = torch.zeros(len(uids), dtype=torch.float32).to(
        self.device
    )

    bt.logging.info(f"[{CHALLENGE_NAME}] Starting evaluation")

    # Compute the score
    for idx, (uid) in enumerate(uids):
        # Get the miner
        miner: Miner = next((miner for miner in self.miners if miner.uid == uid), None)

        bt.logging.info(f"[{CHALLENGE_NAME}][{miner.uid}] Computing score...")
        bt.logging.debug(f"[{CHALLENGE_NAME}][{miner.uid}] Country {miner.country}")

        # Check if the miner is suspicious
        miner.suspicious, miner.penalty_factor = is_miner_suspicious(
            miner, suspicious_uids
        )
        if miner.suspicious:
            bt.logging.warning(f"[{CHALLENGE_NAME}][{miner.uid}] Miner is suspicious")

        # Check if the miner/subtensor are verified
        if not miner.verified or not miner.sync:
            bt.logging.warning(f"[{CHALLENGE_NAME}][{miner.uid}] {reasons[idx]}")

        # Check the miner's ip is not used by multiple miners (1 miner = 1 ip)
        if miner.has_ip_conflicts:
            bt.logging.warning(
                f"[{CHALLENGE_NAME}][{miner.uid}] {miner.ip_occurences} miner(s) associated with the ip"
            )

        # Compute score for availability
        miner.availability_score = compute_availability_score(miner)
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Availability score {miner.availability_score}"
        )

        # Compute score for latency
        miner.latency_score = compute_latency_score(miner, self.miners)
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Latency score {miner.latency_score}"
        )

        # Compute score for performance
        miner.performance_score = compute_performance_score(miner, self.miners)
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Performance score {miner.latency_score}"
        )

        # Compute score for reliability
        miner.reliability_score = await compute_reliability_score(miner)
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Reliability score {miner.reliability_score}"
        )

        # Compute score for distribution
        miner.distribution_score = compute_distribution_score(miner, self.miners)
        bt.logging.debug(
            f"[{CHALLENGE_NAME}][{miner.uid}] Distribution score {miner.distribution_score}"
        )

        # Compute final score
        miner.score = compute_final_score(miner)
        rewards[idx] = miner.score
        bt.logging.info(f"[{CHALLENGE_NAME}][{miner.uid}] Final score {miner.score}")

        # Send the score details to the miner
        miner.version = await send_scope(self, miner)

        # Save miner snapshot in database
        await update_statistics(self, miner)

    bt.logging.trace(f"[{CHALLENGE_NAME}] Rewards: {rewards}")

    # Compute forward pass rewards
    scattered_rewards: torch.FloatTensor = (
        self.moving_averaged_scores.to(self.device)
        .scatter(
            0,
            torch.tensor(uids).to(self.device),
            rewards.to(self.device),
        )
        .to(self.device)
    )
    bt.logging.trace(f"[{CHALLENGE_NAME}] Scattered rewards: {scattered_rewards}")

    # Update moving_averaged_scores with rewards produced by this step.
    # alpha of 0.05 means that each new score replaces 5% of the weight of the previous weights
    alpha: float = 0.1
    self.moving_averaged_scores = alpha * scattered_rewards + (
        1 - alpha
    ) * self.moving_averaged_scores.to(self.device)
    bt.logging.trace(
        f"[{CHALLENGE_NAME}] Updated moving avg scores: {self.moving_averaged_scores}"
    )

    # Suspicious miners - moving weight to 0 for deregistration
    deregister_suspicious_uid(self.miners, self.moving_averaged_scores)
    bt.logging.trace(
        f"[{CHALLENGE_NAME}] Deregistered moving avg scores: {self.moving_averaged_scores}"
    )

    # Display step time
    forward_time = time.time() - start_time
    bt.logging.debug(f"[{CHALLENGE_NAME}] Step finished in {forward_time:.2f}s")

    # Log event
    log_event(self, uids, forward_time)
