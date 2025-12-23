# autoscaler.py
# Environment Variables Required for OpenStack Authentication:
# To create an application credential in OpenStack, see the following guide: https://docs.jetstream-cloud.org/ui/cli/auth/#using-the-horizon-dashboard-to-generate-openrcsh
# The following environment variables must be set in your environment to enable authentication and access to your OpenStack project:
# - OS_AUTH_TYPE: The authentication type to use (e.g., "v3applicationcredential").
# - OS_AUTH_URL: The URL for the OpenStack Identity service (Keystone).
# - OS_IDENTITY_API_VERSION: The version of the Identity API (e.g., "3").
# - OS_REGION_NAME: The name of the OpenStack region to use.
# - OS_INTERFACE: The interface type for endpoint selection (e.g., "public", "internal", "admin").
# - OS_APPLICATION_CREDENTIAL_ID: The application credential ID for authentication.
# - OS_APPLICATION_CREDENTIAL_SECRET: The application credential secret for authentication.
# Ensure these variables are correctly set in your shell environment before running this script to allow successful connection and resource management in your OpenStack project.
import openstack
import time
import datetime
import os
import base64

# This is a simple example of how to run multiple jobs on Jetstream2 using OpenStack API
# The script will launch a new VM for each job in the input_data list.
# Each VM will
# 1. Download the input data from an object store
# 2. Run the job
# 3. Upload the results back to the object store.


# =============================================================================
# PART 1: CONFIGURATION
# =============================================================================

# --- User-configurable settings ---

#  Increase max workers if you want to run more instances at the same time
MAX_WORKERS = 2
#  Increase jobs timeout if you expect your jobs to run longer then 60 minutes
JOB_TIMEOUT = 3600  # 60 minutes

VM_NAME_PREFIX = "openstack-worker-"

# -----------------------------------------------------------------------------
# PART1: Create base clout-init
# -----------------------------------------------------------------------------
VM_NAME_PREFIX = "openstack-worker-"
NETWORK_NAME_1 = "auto_allocated_network"
NETWORK_NAME_2 = "planemo-pulsar"
CHECK_INTERVAL = 30  # seconds

conn = openstack.connect()
# --- OpenStack Authentication (from environment) ---
auth_type = os.environ.get("OS_AUTH_TYPE", "default1")
auth_url = os.environ.get("OS_AUTH_URL", "default1")
identify_api_version = os.environ.get("OS_IDENTITY_API_VERSION", "default1")
region_name = os.environ.get("OS_REGION_NAME", "default1")
interface = os.environ.get("OS_INTERFACE", "default1")
application_credential_id = os.environ.get("OS_APPLICATION_CREDENTIAL_ID", "default1")
application_credential_secret = os.environ.get("OS_APPLICATION_CREDENTIAL_SECRET", "default1")

# --- Instance and Job Configuration ---
# Possible flavors provided by Jetstream2
# https://docs.jetstream-cloud.org/general/instance-flavors/
# m3.medium equeals to 8 vCPUs, 30 GB ram, 60GB local storage with a cost of 8 SU per hour
FLAVOR_NAME = "m3.medium"
# Possible starting images
# https://docs.jetstream-cloud.org/general/featured/
IMAGE_NAME = "Featured-Minimal-Ubuntu24"

# The current run command will only run samtools sort for other applications
# you will want to either change the software listed in packages for cloud_init_str
# or modify build a custom image/snapshot containing the software you need
# https://docs.jetstream-cloud.org/getting-started/snapshots/, this is recommended
# when you have larger sets of dependencies to install.

BASE_CLOUD_INIT_TEMPLATE = f"""
#cloud-config
package_update: true
package_upgrade: true
packages:
  - samtools
  - python3-swiftclient
write_files:
  - path: /etc/profile.d/myenv.sh
    content: |
      export OS_AUTH_TYPE={auth_type}
      export OS_AUTH_URL={auth_url}
      export OS_IDENTITY_API_VERSION={identify_api_version}
      export OS_REGION_NAME={region_name}
      export OS_INTERFACE=${interface}
      export OS_APPLICATION_CREDENTIAL_ID={application_credential_id}
      export OS_APPLICATION_CREDENTIAL_SECRET={application_credential_secret}
users:
  - name: exouser
    plain_text_passwd: testar2020
    lock_passwd: false
    groups: sudo
    shell: /bin/bash
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
runcmd:
"""


# --- Data Configuration ---
# Object keys that will be downloaded from the object store. One tuple will
# be processed per instance
input_data = [
  ("species/Taeniopygia_guttata/bTaeGut1/genomic_data/pacbio/m151218_064724_42161_c100952770310000001823221506251610_s1_p0.subreads.bam",),
  ("species/Taeniopygia_guttata/bTaeGut1/genomic_data/pacbio/m151221_153927_sherri_c100977592550000001823226008101641_s1_p0.subreads.bam",),
  ("species/Taeniopygia_guttata/bTaeGut1/genomic_data/pacbio/m151224_065019_sherri_c100974672550000001823228308031671_s1_p0.subreads.bam",),
]
# Object store names
INPUT_OBJECT_STORE = "genomeark"

# Name of the object store where results will be uploaded.
OUTPUT_OBJECT_STORE = "test-smeds"

# This dictionary tracks servers launched by this script to manage their lifecycle.
server_dict = {}

# =============================================================================
# PART 2: AUTOSCALING AND JOB MANAGEMENT
# =============================================================================

def run_job_manager():
    """
    Main loop to manage the lifecycle of jobs and worker instances.

    This function continuously checks the state of jobs and workers. It launches
    new workers if there are pending jobs and capacity is available. It also
    periodically cleans up terminated or long-running instances. The loop
    exits once all jobs have been submitted and all workers have finished.
    """
    counter_input_submitted = 0
    while True:
        # Create new instance if we have less active workers
        # then max workers `MAX_WORKERS > len(list_active_workers())` and
        # if we haven't processed all input data `len(input_data) > counter_input_submitted)`
        while (MAX_WORKERS > len(list_active_workers()) \
            and len(input_data) > counter_input_submitted):
            name = f"{VM_NAME_PREFIX}{int(time.time())}-index{counter_input_submitted}"
            launch_worker(
                name,
                counter_input_submitted,
            )
            counter_input_submitted += 1
            # Make sure create instance has time to get into active state
            time.sleep(CHECK_INTERVAL)

        # Check on running instances and see if any have been running for too long
        for k in [keys for keys in server_dict]:
            kill_long_running_job(server_dict[k], max_running_time=JOB_TIMEOUT)
        clean_up_servers() 
        print_active_workers()
        time.sleep(30)
        # If we have started processing all input data and there is no more active workers
        # we can exit the autoscaler
        if len(input_data) <= counter_input_submitted and len([s for s in conn.compute.servers() if s.name.startswith(VM_NAME_PREFIX)]) == 0:
            break

def launch_worker(name, index):
    """
    Launches a new OpenStack server instance to run a job.

    Args:
        name (str): The name for the new server.
        index (int): The index of the job in the `input_data` list.
    """
    run_command_string = create_run_command(index, input_data, INPUT_OBJECT_STORE, OUTPUT_OBJECT_STORE)
    full_cloud_init = BASE_CLOUD_INIT_TEMPLATE + run_command_string

    print(f"Creating VM {name}")
    server = conn.compute.create_server(
        name=name,
        image_id=conn.compute.find_image(IMAGE_NAME).id,
        flavor_id=conn.compute.find_flavor(FLAVOR_NAME).id,
        networks=[{"uuid": conn.network.find_network(NETWORK_NAME_1).id}],
        config_drive=True,
        user_data=base64.b64encode(full_cloud_init.encode("utf-8")).decode('utf-8'))
    # print(f"With command:\n {full_cloud_init}")
    server_dict[server.name] = server


# =============================================================================
# PART 3: COMMAND GENERATION
# =============================================================================

def create_download_data(index, data, object_store_name):
    """
    Generates a shell command to download files from an object store using 'swift', and 
    returns the command along with a list of local filenames.

    Args:
        index (int): The index to select a subset of files from the 'data' list.
        data (list of tuples): A list where each element is a tuple of object keys to be downloaded.
        object_store_name (str): The name of the object store container from which files will be downloaded.

    Returns:
        tuple:
            download_command (str): A shell command string that downloads each file in the selected subset using 'swift download'.
            input_files (list of str): A list of local filenames (basenames of the files to be downloaded).
    """
    download_command = ""
    input_files = []
    for f in data[index]:
        input_files.append(os.path.basename(f))
        download_command += f" && swift download {object_store_name} {f} -o {input_files[-1]} "
    return download_command, input_files

def create_upload_data(output_files, output_object_store):
    """
    Constructs a shell command string to upload multiple output files to an object 
    store using the 'swift upload' command.

    Args:
        output_files (tuples of str): tuples of all paths to be uploaded.
        output_object_store (str): Name of the target object store container.

    Returns:
        str: A shell command string that uploads each file in 'output_files' to 
        'output_object_store' using segmented uploads.
    """
    upload_command = ""
    for of in output_files:
        upload_command += f" && swift upload {output_object_store} {of} --segment-container test-smeds_segments -S 5000000000"
    return upload_command

def create_run_command(index, input_data, input_object_store_name, output_object_store_name):
    """
    Constructs the full shell command to be executed on the VM, including:
    1. Downloading input files from the object store.
    2. Running the job (samtools sort).
    3. Uploading results to the output object store.
    4. Powering off the VM after completion.

    Args:
        index (int): Index of the job/input data.
        input_data (list of tuples): List of tuples containing input object keys.
        input_object_store_name (str): Name of the input object store.
        output_object_store_name (str): Name of the output object store.

    Returns:
        str: The full shell command to be run via cloud-init.
    """
    # Generate command to download input files and get their local filenames
    input_command, input_files = create_download_data(index, input_data, input_object_store_name)
    # Command to create results directory and run samtools sort on the input files
    run_command = f" && mkdir result{index} && samtools sort -@ 8 " + " ".join(input_files) + f" -o result{index}/sorted.{index}.bam "
    # Command to upload results directory to the output object store
    upload_command = create_upload_data((f"result{index}/", ), output_object_store_name)
    # Combine all commands, set up environment, and power off VM after job completion
    return (
        '  - sudo -u exouser bash -c "'
        + "source /etc/profile.d/myenv.sh; cd /home/exouser; "
        + input_command
        + run_command
        + upload_command
        + '; echo poweroff && sudo poweroff -f"  &'
    )

# =============================================================================
# PART 4: HELPER AND MAINTENANCE FUNCTIONS
# =============================================================================

def clean_up_servers():
    """
    Finds and deletes servers managed by this script that are in a 'SHUTOFF' state.
    It also removes them from the internal tracking dictionary.
    """
    for s in conn.compute.servers():
        if s.name.startswith(VM_NAME_PREFIX) and s.status == "SHUTOFF":
            print(f'Removing server ({s.id}, {s.name}) with status {s.status} ... ', end="")
            server = conn.compute.get_server(s.id)
            conn.compute.delete_server(server)
            conn.compute.wait_for_delete(server)
            if server.name in server_dict:
                del server_dict[server.name]
            print(" ... removed!!!")

def kill_long_running_job(server, max_running_time=3600):
    """
    Deletes a server if its uptime exceeds a specified maximum duration.

    This acts as a failsafe to prevent runaway instances from incurring
    unnecessary costs.

    Args:
        server (openstack.compute.v2.server.Server): The server object to check.
        max_running_time (int): The maximum allowed uptime in seconds.
    """
    now = datetime.datetime.now(datetime.UTC)
    s = conn.compute.get_server(server.id)
    launched = datetime.datetime.strptime(s.created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    uptime = (now - launched).total_seconds()
    if uptime > max_running_time:
        print(f"Deleting idle VM {server.name} ...", end="")
        conn.compute.wait_for_delete(conn.compute.delete_server(server.id))
        print("removed")
        del server_dict[server.name]

def list_active_workers():
    """
    Returns a list of active worker servers managed by this script.

    Returns:
        list: A list of server objects with names matching the prefix and status 'ACTIVE'.
    """
    return [s for s in conn.compute.servers() if s.name.startswith(VM_NAME_PREFIX) and s.status == "ACTIVE"]

def print_active_workers():
    """Prints the current count of active workers."""
    print(f"Active workers: {len(list_active_workers())}")


if __name__ == "__main__":
    try:
        run_job_manager()
    finally:
        print("Job manager finished. Performing final cleanup.")
        clean_up_servers()
