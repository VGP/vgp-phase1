# Different Options for Accessing GenomeArk Object Storage on Jetstream2

[Google Slides}(https://docs.google.com/presentation/d/1tZmgUFDOhFhePVD7Y35mguiUyQSWyKfg_OZrNFrlJQI/edit?usp=sharing)

The GenomeArk object storage hosted on Jetstream is publicly accessible and supports multiple access methods. Here's a few examples.

# AWS Command Line Interface

The AWS Command Line Interface (AWS CLI) is a unified tool to manage your AWS services from the command line. It provides direct access to the public APIs of AWS services and can be used to interact with S3-compatible object storage systems. While primarily designed for AWS, it works well with other S3-compatible storage services like Jetstream2.

## Requirements

- [aws CLI](https://aws.amazon.com/cli/)

Installation instructions can be found at [getting-started-install.html](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Configure

To simplify usage, you can set up an alias. An alias is a shortcut command that allows you to avoid typing long or repetitive commands. Here, the alias will handle most of the configuration arguments for you.
```bash
alias s3js2='aws s3 --endpoint-url https://js2.jetstream-cloud.org:8001 --no-sign-request '
```

## Useful commands

```bash
s3js2 ls s3://genomeark/species/Abramis_brama/fAbrBra2/assembly_curated/
s3js2 cp s3://genomeark/species/Abramis_brama/fAbrBra2/assembly_curated/fAbrBra2.pri.cur.20240502.chromosomes.csv.gz  fAbrBra2.pri.cur.20240502.chromosomes.csv.gz

```

Additional commands can be found at [https://docs.aws.amazon.com/cli/latest/reference/s3/](https://docs.aws.amazon.com/cli/latest/reference/s3/)

# s3fs

s3fs is a FUSE-based file system that allows you to mount an S3 bucket as a local file system on your machine. Using s3fs, you can interact with the object storage as if it were a local directory, enabling seamless access of files.

## Requirements

- s3fs

```bash
## debian/ubuntu
sudo apt update
sudo apt install s3fs

## centos/rhel
sudo yum install epel-release
sudo yum install s3fs-fuse

## macOS (homebrew)
brew install s3fs
```

## Mount bucket

This command will mount the bucket to a folder named ga2.

 ```bash
 mkdir ga2
 s3fs genomeark ga2   -o url=https://js2.jetstream-cloud.org:8001   -o use_path_request_style -o public_bucket=1
 ```

# Rclone

Rclone is a command-line program to manage files on cloud storage. It's a feature-rich alternative to cloud vendors' web storage interfaces. Over 40 cloud storage products support rclone including S3 object stores, business & consumer file storage services, as well as standard transfer protocols. For detailed documentation and examples, visit [rclone.org](https://rclone.org/)

## Requirments

- rclone

```bash
## debian/ubuntu
sudo apt update
sudo apt install rclone

## centos/rhel
sudo yum install epel-release
sudo yum install rclone

## macOS (homebrew)
brew install rclone
```

## Configuration file

Found at `~/.config/rclone/rclone.conf`
```
[genomeark-js2]
type = s3
provider = Other
env_auth = false
access_key_id =
secret_access_key =
region = IU
endpoint = https://js2.jetstream-cloud.org:8001
acl = public-read
```

## Mount bucket

This command will mount the bucket to a folder named ga2.

```bash
mkdir ga2
rclone mount genomeark-js2:genomeark ga2 &  
```

## Useful commands

```bash
rclone ls genomeark-js2:genomeark/species/Abramis_brama/fAbrBra2/assembly_curated/
rclone copy genomeark-js2:genomeark/species/Abramis_brama/fAbrBra2/assembly_curated/fAbrBra2.pri.cur.20240502.chromosomes.csv.gz  fAbrBra2.pri.cur.20240502.chromosomes.csv.gz
rclone cat genomeark-js2:genomeark/species/Abramis_brama/fAbrBra2/genomic_data/arima/re_bases.txt
```

Additional commands can be found at [https://rclone.org/commands/](https://rclone.org/commands/)

# python

You can also access the data using Python libraries such as boto3. This repository includes a Python script that demonstrates how files can be accessed and read from the object store.

See [access_object_storage.py](access_object_storage.py) for an example of how to access files using Python.

# HTTP Access 

The bucket can also be accessed using your regular browser:
 - list all objects: https://js2.jetstream-cloud.org:8001/genomeark
 - access a file: https://js2.jetstream-cloud.org:8001/genomeark/species/Abramis_brama/fAbrBra2/genomic_data/arima/re_bases.txt
