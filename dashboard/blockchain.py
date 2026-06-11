from web3 import Web3
from django.conf import settings
import json
import os

#  WEB3
w3 = Web3(Web3.HTTPProvider(
    settings.ALCHEMY_POLYGON_AMOY,
    request_kwargs={'timeout': 60}
))

#  LOAD ABI
abi_path = os.path.join(settings.BASE_DIR, "dashboard", "abi", "DigitalWill.json")

with open(abi_path, "r") as f:
    contract_json = json.load(f)

abi = contract_json.get("abi", contract_json)

# CONTRACT
def get_contract():
    return w3.eth.contract(
        address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
        abi=abi
    )


#  1. SET INHERITANCE
def set_inheritance_on_chain(beneficiary_address, amount):
    try:
        print("CALLING setInheritance")

        contract = get_contract()
        account = w3.eth.account.from_key(settings.OWNER_PRIVATE_KEY)

        print("FROM:", account.address)
        print("TO:", beneficiary_address)
        print("AMOUNT:", amount)

        tx = contract.functions.setInheritance(
    Web3.to_checksum_address(beneficiary_address),
    int(amount)
).build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address, "pending"),
    "gas": 300000,
    "gasPrice": w3.to_wei("30", "gwei"),
    "chainId": 80002   # 🔥 AMOY CHAIN ID
})

        signed = w3.eth.account.sign_transaction(tx, settings.OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print("TX SENT:", tx_hash.hex())

        return tx_hash.hex()

    except Exception as e:
        print(" ERROR in setInheritance:", str(e))
        raise e


#  2. CONFIRM DEATH
def confirm_death_on_chain():
    try:
        print(" CALLING confirmDeath")

        contract = get_contract()
        account = w3.eth.account.from_key(settings.OWNER_PRIVATE_KEY)

        print("FROM:", account.address)

        tx = contract.functions.confirmDeath().build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address, "pending"),
    "gas": 200000,
    "gasPrice": w3.to_wei("30", "gwei"),
    "chainId": 80002
})
        print("RPC:", settings.ALCHEMY_POLYGON_AMOY)
        print("FROM:", account.address)

        signed = w3.eth.account.sign_transaction(tx, settings.OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(" DEATH TX:", tx_hash.hex())

        return tx_hash.hex()

    except Exception as e:
        print(" ERROR in confirmDeath:", str(e))
        raise e


#  3. CLAIM (BY BENEFICIARY)
def claim_inheritance_on_chain(private_key):
    contract = get_contract()
    account = w3.eth.account.from_key(private_key)

    tx = contract.functions.claimInheritance().build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address, "pending"),
        "gas": 200000,
        "gasPrice": w3.to_wei("30", "gwei"),
    })

    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    return tx_hash.hex()