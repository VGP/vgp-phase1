import boto3
import os
import smart_open

from botocore import UNSIGNED
from botocore.config import Config
import logging

log = logging.getLogger(__name__)


def _write_file(output, bucket_uri, decompress, client):
    """
    Writes data from an S3 object to a file-like output object.

    Args:
        output: A file-like object that supports write operations.
        bucket_uri (str): The S3 URI of the object to read from.
        decompress (bool): Whether to decompress compressed files during read.
            If True, compressed files (e.g., .gz) will be decompressed.
            If False, files are read as-is without decompression.
        client: The S3 client object to use for the operation.

    Notes:
        - Uses smart_open library for handling S3 objects
        - Reads data in chunks of 8192 bytes for memory efficiency
        - Only affects compressed files - uncompressed files are read as-is
    """

    with smart_open.open(
        bucket_uri, 'rb',
        compression='disable' if not decompress else 'infer_from_extension',
        transport_params={'client': client}
    ) as s3_file:
        while True:
            chunk = s3_file.read(8192)
            if not chunk:
                break
            output.write(chunk)


def fetch_file_from_bucket(file_key, output_file, endpoint="https://js2.jetstream-cloud.org:8001", bucket="genomeark", decompress=False):
    """Downloads a file from an S3-compatible object storage bucket.

    This function handles both regular and segmented files from S3 storage. For segmented files,
    it automatically downloads and combines all segments into a single output file.

    Args:
        file_key (str): The key/path of the file in the bucket
        output_file (str): Local path where the downloaded file should be saved
        endpoint (str, optional): S3 endpoint URL. Defaults to "https://js2.jetstream-cloud.org:8001"
        bucket (str, optional): Name of the S3 bucket. Defaults to "genomeark"
        decompress (bool, optional): Whether to decompress the file while downloading. Defaults to False

    Returns:
        None

    Raises:
        boto3.exceptions.Boto3Error: If there are issues with the S3 client operations
        OSError: If there are issues creating directories or writing the output file

    Notes:
        - Uses unsigned authentication for public bucket access
        - Automatically creates parent directories for the output file if they don't exist
        - Handles segmented objects by downloading and combining all segments in order
    """
    session = boto3.Session()
    client = session.client(
        's3',
        endpoint_url=endpoint,  # Your custom endpoint
        config=Config(signature_version=UNSIGNED)  # Use unsigned signature for public access
    )
    response = client.head_object(
        Bucket=bucket_name,
        Key=file_key
    )
    segmented_object = response['ResponseMetadata']['HTTPHeaders'].get('x-object-manifest')
    parentdir = os.path.dirname(output_file)
    if parentdir:
        log.debug(f"Creating parent folder: {parentdir}")
        os.makedirs(parentdir, parent=True)
    with open(output_file, 'wb') as out_file:
        if not segmented_object:
            bucket_uri = f"s3://{bucket}/{file_key}"
            log.debug(f"Fetching file: {file_key}, writing {output_file}")
            _write_file(out_file, bucket_uri, decompress, client)
        else:
            response = client.list_objects_v2(Bucket=f'{bucket_name}_segments', Prefix=key_fasta)
            segments = sorted(response.get('Contents', []), key=lambda obj: obj['Key'])
            log.debug(f"Fetching segmented file: {file_key}, writing {output_file}")
            for segment in segments:
                segment_key = segment['Key']
                bucket_uri = f"s3://{bucket}_segments/{segment_key}"
                log.debug(f"Downloading segment: {segment_key}")
                _write_file(out_file, bucket_uri, decompress, client)


# Fetch small txt file
fetch_file_from_bucket(
    "species/Abramis_brama/fAbrBra2/genomic_data/arima/re_bases.txt",
    "re_bases.txt"
)
# Fetch Small fasta
fetch_file_from_bucket(
    "species/Abramis_brama/fAbrBra2/assembly_curated/fAbrBra2.pri.cur.20240502.fasta.gz",
    "fAbrBra2.pri.cur.20240502.fasta.gz"
)
# Fetch Small fasta  and decompress is
fetch_file_from_bucket(
    "species/Abramis_brama/fAbrBra2/assembly_curated/fAbrBra2.pri.cur.20240502.fasta.gz",
    "fAbrBra2.pri.cur.20240502.fasta",
    decompress=True
)
# Fetch big fasta file which has been splited into segments
fetch_file_from_bucket(
    'species/Lissotriton_vulgaris/aLisVul1/assembly_cambridge/aLisVul1.pri.asm.20240102.fasta.gz',
    'aLisVul1.pri.asm.20240102.fasta.gz'
)
