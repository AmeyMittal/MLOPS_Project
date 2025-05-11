This folder provides scripts to provision:

--**Object Storage**: Using OpenStack CLI.


--**Block Storage**: Using the python-chi library.

#Prerequisites


Chameleon Cloud Account: Ensure you have an active account.

OpenStack RC File: Download your CHI@TACC-openrc.sh from the Chameleon dashboard and place it in ~/chi/.

Chameleon VM Instance: Launch a VM instance on Chameleon Cloud where you'll execute these scripts.


File Structure

StudyBot-Audio-Captioning-and-Q-A-chatbot-/
├── infrastructure/
│   ├── provision_block_storage.py
│   └── provision_object_storage.sh
|   ├── README.md
└── ...


Provisioning Steps

1. **Object Storage**
   
This script creates an object storage container named object-storage-project48.

Run the script:

bash infrastructure/provision_object_storage.sh

2. **Block Storage**
   
This script provisions a 30GB block storage volume named block-persist-project48 on the KVM@TACC site.

Run the script:

pip install python-chi
python3 infrastructure/provision_block_storage.py

Verification

Object Storage: Check the container:

  openstack container list

Block Storage: Verify the volume:

  openstack volume list
