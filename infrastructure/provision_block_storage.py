from chi import use_site, clients

# Set site to KVM for block storage
use_site("KVM@TACC")

# Obtain the Cinder client
cinder = clients.cinder()

# Create the volume
volume = cinder.volumes.create(
    size=30,  # Size in GB
    name="block-persist-project48",
    volume_type="standard"
)

print(f" Created volume: {volume.name}, Size: {volume.size}GB")