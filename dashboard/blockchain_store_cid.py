from web3 import Web3
from django.conf import settings
import json

RPC = "https://polygon-amoy.g.alchemy.com/v2/-5KAoOccnCfxFDiO-kKpX"
       

def store_cid_on_chain(contract_address, cid, metadata):

    w3 = Web3(Web3.HTTPProvider(RPC))

    with open("static/abi/DigitalWill.json") as f:
        contract_json = json.load(f)

    abi = contract_json["abi"]

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=abi
    )

    account = w3.eth.account.from_key(settings.OWNER_PRIVATE_KEY)

    txn = contract.functions.setWillData(
        cid,
        metadata
    ).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300000,
        "gasPrice": w3.to_wei("30", "gwei")
    })

    signed = w3.eth.account.sign_transaction(txn, settings.OWNER_PRIVATE_KEY)

    tx = w3.eth.send_raw_transaction(signed.rawTransaction)

    return tx.hex()