Running analyses on Jetstream2 and accessing the genomeark2 bucket is straightforward.
In this README, we'll guide you through launching an instance—either a preconfigured one or a clean instance that you can configure yourself.

We'll focus on using Planemo, a command-line tool for interacting with Galaxy, but you're free to use the tool of your choice. Planemo be used to either start an analysis on a Galaxy instance or to run the workflow locally.

The following is an overview of the steps we will perform:

 1. Configure access [SSH or Phassprahes](https://docs.jetstream-cloud.org/ui/exo/access-instance/?h=)
 2. [Create an instance](https://docs.jetstream-cloud.org/ui/exo/create_instance/) using Exosphere 
 3. [Create and mount a workspace volume](https://docs.jetstream-cloud.org/ui/exo/storage/)
 4. Run planemo 

# Configure access SSH or Phassprahes

Instructions for how to access instance can be found here [Accessing an Exosphere Instance](https://docs.jetstream-cloud.org/ui/exo/access-instance/?h=)
and we would recommend that you set up SSH keys. Which can easaly be done by clicking the create button and then selecting SSH Public Key.

![Add public key](./images/upload_ssh_key.png)
# Create instance

Instruction for how to create a new instance cound be found at [Create an instance](https://docs.jetstream-cloud.org/ui/exo/create_instance/) at Exosphere. It's really simple and you will
basically follow these steps:

 1. Click Create button --> Instance
 2. Select source
    - By type --> Create a clean instance (recommended is Ubuntu)  
    - By Image --> Planemo-V0-75-30-20250522
 3. Create Instance
    - Select Flavor: m3.large
    - Choose previously uploaded SSH key

## Configure instance

If you choose to create a clean instance you will need to do some configurerion to mount  the
`genomeark bucket` and to install planemo.

### Install dependencies

```bash
sudo apt-get install -y \
   autoconf \
   automake \
   cryptsetup \
   fuse2fs \
   git \
   fuse \
   libfuse-dev \
   libseccomp-dev \
   libtool \
   pkg-config \
   runc \
   squashfs-tools \
   squashfs-tools-ng \
   uidmap \
   wget \
   zlib1g-dev \
   libsubid-dev \
   python3-lib2to3 \
   s3fs \
   btop
```

### Mount genomeark bucket

To mount the genomeark bucket to a folder you will need to have installed `s3fs`, see previous step.
You will then create the following file `/etc/systemd/system/mount-genomeark-js2.service` with content:

```bash
[Unit]
Description=Mount genomeark S3 bucket using s3fs
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/s3fs genomeark /genomeark-js2 -o url=https://js2.jetstream-cloud.org:8001 -o use_path_request_style -o allow_other -o public_bucket=1 -o uid=1001 -o gid=1001
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
```

We will then create the folder we intead to mount the bucket to and ask the system to apply the file, mount the bucket, and lastly make sure that the folder is mount after a reboot.
```bash
sudo mkdir /genomeark-js2
# Apply the new system file
sudo systemctl daemon-reexec
sudo systemctl enable mount-genomeark-js2.service
# Make sure that the configuration is run after a boot.
sudo systemctl start mount-genomeark-js2.service
```

### Install Singularity

To solve workflow dependencies galaxy/planemo can use singularity, which also can
be used to run a temporary postgres database. A posgres database may be neccessary when running more
complexed workflows locally, where you workflow otherwice could end prematiorly due to a locked database.

To compile singularity you will need to install GO version 1.24
```bash
export VERSION=1.24.1 OS=linux ARCH=amd64 && \
  wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
  sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
  rm go$VERSION.$OS-$ARCH.tar.gz

echo 'export PATH=/usr/local/go/bin:$PATH' >> ~/.bashrc && \
  source ~/.bashrc
```

Install singularity 4.3.0
```bash
export VERSION=4.3.0 && \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz && \
    tar -xzf singularity-ce-${VERSION}.tar.gz && \
    cd singularity-ce-${VERSION}

./mconfig && \
    make -C builddir && \
    sudo make -C builddir install

cd ..

rm -r singularity-ce-${VERSION}*
```

More detailed instructions can be found at [sylabs quick start](https://docs.sylabs.io/guides/latest/user-guide/quick_start.html)

### Install conda

To solve workflow dependencies galaxy/planemo can conda, which then need to be installed.

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh
# When asked to add conda to auto initate using bashrc -- skip it
bash Miniforge3-Linux-$(uname -m).sh
```

### Install planemo

```bash
sudo python3 -m venv /opt/planemo
sudo chown exouser -R /opt/planemo/
source /opt/planemo/bin/activate
pip3 install planemo==0.75.30 galaxy-job-config-init

```

Configure system to autamtically add planemo to the PATH during both by
creating the following file `/etc/profile.d/custom_path.sh` and adding the following content
```bash
#!/bin/sh
export PATH="/opt/planemo/bin/:$PATH"
sudo chmod +x /etc/profile.d/custom_path.sh
```


# Create workspace volume

When we run analysis on the server we may need to use a lot of storage during and
after the analysis is done. We can easaly mount extra storage to the instance by following the
steops found at [Using Storage Under Exosphere](https://docs.jetstream-cloud.org/ui/exo/storage/).
For the example data we recommend that you create a volume with size of atleast 100GB. If you name it
`workspace` you later be able to find it on your instance at `/media/volume/workspace/`.


# Runing planemo

Planemo can be run in multiple ways and we will running it locally on the instance, more information
can be foun at [Planemo --> Running Galaxy workflows](https://planemo.readthedocs.io/en/latest/running.html)

The include example will be running a workflow named [PretextMap Generation from 1 or 2 haplotypes](https://iwc.galaxyproject.org/workflow/hi-c-contact-map-for-assembly-manual-curation-main/) and use data located on
`genomeark bucket`. 

Follow these commands to run planemo:
```bash
# Go to your mounted volume
cd /media/volume/workspace/

# Create a temp folder
mkdir temp
# Folder where the final result will end up
mkdir result

TMPDIR="/media/volume/workspace/temp/" planemo run \
  ~/example_workflow/hi-c-map-for-assembly-manual-curation.ga \
  ~/example_workflow/hi-c-map-for-assembly-manual-curation-job.yaml \
  --database_type postgres_singularity \
  --biocontainers --galaxy_branch v24.2.3  \
  --download_outputs \
  --output_directory result \
  --job_config_file ~/example_workflow/job_conf.yaml
```

This will do the following.

1. run workflow `hi-c-map-for-assembly-manual-curation.ga`
2. use input information found in `hi-c-map-for-assembly-manual-curation-job.yaml`
3. use a postgres database ran in with singularity `--database_type postgres_singularity`
4. use biocontainer to try to solve dependencies `--biocontainers`
5. download the created output `--download_outputs`
6. specify download folder to result `--output_directory result`
7. specify resource usage (a very simple version) `--job_config_file ~/example_workflow/job_conf.yaml`

## Example files

Content of `hi-c-map-for-assembly-manual-curation-job.yaml`
```yaml
Haplotype 1:
  class: File
  filetype: fasta.gz
  path: /genomeark-js2/species/Taeniopygia_guttata/bTaeGut2/assembly_curated/bTaeGut2.hap1.cur.20220905.fasta.gz
Haplotype 2:
  class: File
  filetype: fasta.gz
  path: /genomeark-js2/species/Taeniopygia_guttata/bTaeGut2/assembly_curated/bTaeGut2.hap2.cur.20220905.fasta.gz
Hi-C reads:
  class: Collection
  collection_type: list:paired
  elements:
    - class: Collection
      type: paired
      identifier: Hi-C reads
      elements:
      - identifier: forward
        class: File
        path: /genomeark-js2/species/Taeniopygia_guttata/bTaeGut2/genomic_data/arima/bTaeGut2_ARI8_001_USPD16084394-AK5146_HJFMFCCXY_L1_R1.fq.gz
        filetype: fastqsanger.gz
      - identifier: reverse
        class: File
        path: /genomeark-js2/species/Taeniopygia_guttata/bTaeGut2/genomic_data/arima/bTaeGut2_ARI8_001_USPD16084394-AK5146_HJFMFCCXY_L1_R2.fq.gz
        filetype: fastqsanger.gz
PacBio reads:
  class: Collection
  collection_type: list
  elements:
  - class: File
    identifier: PacBio reads.fastq.gz
    path: /genomeark-js2/species/Taeniopygia_guttata/bTaeGut2/genomic_data/pacbio_hifi/m54306U_210519_154448.hifi_reads.fastq.gz
Do you want to add suffixes to the scaffold names?: true
Will you use a second haplotype?: false
First Haplotype suffix: H1
Second Haplotype suffix: H2
Do you want to trim the Hi-C data?: true
Telomere repeat to suit species: CCCTAA
```

Content of `job_conf.yaml`
```yaml
runners:
  local:
    load: galaxy.jobs.runners.local:LocalJobRunner
    workers: 4

execution:
  default: local_single
  environments:
    local_single:
      runner: local
      docker_enabled: true
      conda_enabled: true
      conda_exec: ~/miniforge3/bin/conda
    local_multi_2:
      runner: local
      local_slots: 2
      docker_enabled: true
      conda_enabled: true
      conda_exec: ~/miniforge3/bin/conda
    local_multi_4:
      runner: local
      local_slots: 4
      docker_enabled: true
      conda_enabled: true
      conda_exec: ~/miniforge3/bin/conda
    local_multi_8:
      runner: local
      local_slots: 8
      docker_enabled: true
      conda_enabled: true
      conda_exec: ~/miniforge3/bin/conda
    local_multi_14:
      runner: local
      local_slots: 14
      docker_enabled: true
      conda_enabled: true
      conda_exec: ~/miniforge3/bin/conda

tools:
 - id: bwa_mem2
   environment: local_multi_14
 - id: minimap2
   environment: local_multi_8
 - id: cutadapt
   environment: local_multi_2
 - id: samtools_merge
   environment: local_multi_4

```

