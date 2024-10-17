#!/bin/bash

# Check if the user want to generate or re-generate a coldkey
read -p "Do you want to (re-)generate a coldkey (yes/no)? " ACTION_ON_COLDKEY
if [ "$ACTION_ON_COLDKEY" != "yes" ] && [ "$ACTION_ON_COLDKEY" != "no" ]; then
    echo -e "\\e[31mThe possible choices are 'yes' or 'no'.\\e[0m"
    exit 1
fi

if [[ $ACTION_ON_COLDKEY == "yes" ]]; then
    read -p "Do you want to generate a new coldkey (yes/no)? " NEW_COLDKEY
    read -p "Enter the wallet name: " WALLET_NAME
    
    if [[ $NEW_COLDKEY == 'no' ]]; then
        read -p "Enter mnemonic, seed, or json file location for the coldkey? " COLDKEY_MNEMONIC
    fi
else
    read -p "Enter the wallet name: " WALLET_NAME
fi

# Check if the user want to generate or re-generate a hotkey
read -p "Do you want to (re-)generate a hotkey (yes/no)? " ACTION_ON_HOTKEY
if [ "$ACTION_ON_HOTKEY" != "yes" ] && [ "$ACTION_ON_HOTKEY" != "no" ]; then
    echo -e "\\e[31mThe possible choices are 'yes' or 'no'.\\e[0m"
    exit 1
fi

if [[ $ACTION_ON_HOTKEY == "yes" ]]; then
    read -p "Do you want to generate a new hotkey (yes/no)? " NEW_HOTKEY
    read -p "Enter the hotkey name: " HOTKEY_NAME
    
    if [[ $NEW_HOTKEY == 'no' ]]; then
        read -p "Enter mnemonic, seed, or json file location for the hotkey? " HOTKEY_MNEMONIC
    fi
fi

# (Re-)Generate coldkey
if [[ $ACTION_ON_COLDKEY == 'yes' ]]; then
    if [[ $NEW_COLDKEY == 'yes' ]]; then
        # Generate a new coldkey
        btcli w new_coldkey --wallet.name $WALLET_NAME
    else
        # Re-generate an existing coldkey
        btcli w regen_coldkey --wallet.name $WALLET_NAME --mnemonic $COLDKEY_MNEMONIC
    fi
fi

# (Re-)Generate hotkey
if [[ $ACTION_ON_HOTKEY == 'yes' ]]; then
    if [[ $NEW_HOTKEY == 'yes' ]]; then
        # Generate a new hotkey
        btcli w new_hotkey --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME
    else
        # Re-generate an existing hotkey
        btcli w regen_hotkey --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME --mnemonic $HOTKEY_MNEMONIC
    fi
fi