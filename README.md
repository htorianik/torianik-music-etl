## torianik-music-etl

### Abstract

[Dataset](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge)

C.W. Chen, P. Lamere, M. Schedl, and H. Zamani. Recsys Challenge 2018: Automatic Music Playlist Continuation. In Proceedings of the 12th ACM Conference on Recommender Systems (RecSys ’18), 2018.

### Deploy

1. Create `.tfvars`:
```
account_id=<your aws account id>
project_name=<name of your porject>
subnet_id=<subnet with NAT>
secondary_subnet_id=<any other subnet in different AZ>
security_group_id=<security group you want to create db instance and glue connection in>
```
2. Configure AWS client with region and creds:
```bash
$ export AWS_PROFILE=<my-aws-profile>
$ export AWS_REGION=<my-region>
```
3. Init and apply changes with terraform:
```bash
$ terraform init -var-file .tfvars
$ terraform apply -var-file .tfvars
```

### Execution
*Not tested, used UI insted.*

*Naming is correct only if you did not override default variables.*

```
$ ./utils/unpack \
    --prefix /raw \
    --input <local/path/to/archive> \
    --bucket <your-account-id>-torianik-music-dev-data-lake
$ aws glue start-crawler --name torianik-music-dev-crawler  # wait until crawler finishes
$ aws glue get-tables --database-name torianik-music-dev-database  # find out name of the created table 
$ aws glue start-job-run \
    --job-name torianik-music-dev-etl-job \
    --arguments catalog_table=<table-from-the-previous-command-here>  # start the etl job
```

### Development
```bash
cd dev
./build_image.sh
./run.sh
```