#!/bin/bash

# Check if the user want to generate or re-generate a hotkey
read -p "Do you want to remove a hotkey (yes/no)? " ACTION_ON_HOTKEY
if [ "$ACTION_ON_HOTKEY" != "yes" ] && [ "$ACTION_ON_HOTKEY" != "no" ]; then
    echo -e "\\e[31mThe possible choices are 'yes' or 'no'.\\e[0m"
    exit 1
fi

if [[ $ACTION_ON_HOTKEY == "yes" ]]; then
    read -p "Enter the hotkey name: " HOTKEY_NAME
    
    # Remove the hotkey
    dir="~/.bittensor/wallets/$HOTKEY_NAME/hotkey"
    if [ -d "$dir" ]; then
        rm -rf $dir
        echo -e "\e[32mHotkey $HOTKEY_NAME removed successfully\e[0m"
    fi
fi

# Check if the user want to generate or re-generate a coldkey
read -p "Do you want to remove a coldkey (yes/no)? " ACTION_ON_COLDKEY
if [ "$ACTION_ON_COLDKEY" != "yes" ] && [ "$ACTION_ON_COLDKEY" != "no" ]; then
    echo -e "\\e[31mThe possible choices are 'yes' or 'no'.\\e[0m"
    exit 1
fi

if [[ $ACTION_ON_COLDKEY == "yes" ]]; then
    read -p "Enter the wallet name: " WALLET_NAME
    
    # Remove the coldkey
    file=~/.bittensor/wallets/$WALLET_NAME/coldkey
    if [ -e "$file" ]; then
        rm -f $file
    fi
    
    # Remove the coldkey pub
    file=~/.bittensor/wallets/$WALLET_NAME/coldkeypub.txt
    if [ -e "$file" ]; then
        rm -f $file
    fi
    
    echo -e "\e[32mColdkey $WALLET_NAME removed successfully\e[0m"
fi

# Check if everything has been removed and remove the wallet
if [ -n "$WALLET_NAME" ] && [ ! "$(ls -A "$dir")" ]; then
    dir=~/.bittensor/wallets/$WALLET_NAME
    if [ -d "$dir" ]; then
        rmdir $dir
    fi
fi