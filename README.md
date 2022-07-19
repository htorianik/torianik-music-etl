## torianik-music-etl

### Abstract
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

AWS Glue PySpark ETL pipeline fully managed by terraform. Converst JSON dataset to SQL database hosted on RDS instance.

### Dataset

[Dataset](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge)

C.W. Chen, P. Lamere, M. Schedl, and H. Zamani. Recsys Challenge 2018: Automatic Music Playlist Continuation. In Proceedings of the 12th ACM Conference on Recommender Systems (RecSys ’18), 2018.

#### Architecture

![torianik music diagram](https://github.com/htorianik/torianik-music-etl/blob/main/doc/torianik-music.drawio.png)

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
$ # Start a crawler
$ aws glue start-crawler --name torianik-music-dev-crawler
$ # Wait unitl crawler state is READY
$ aws glue get-crawler --name torianik-music-dev-crawler --query "Crawler.State" --output text
$ # Retrieve a name of the catalog table created
$ aws glue get-tables --database-name torianik-music-dev-database --query "TableList[*].Name" --output text
$ # Start a job
$ aws glue start-job-run \
    --job-name=torianik-music-dev-etl-job \
    --arguments='--catalogTable=<table you received from the previous command>'
```

### Development
First thing first, follow [Deploy](#Deploy) section.
```bash
cd dev
./build_image.sh
./run.sh
```

### TODO
* Enhance the developemnt flow. Add role assumption in the glue container.
* Sync requirements between terraform and requirements.txt file.
* Make the diagram prettier.
* Currently us-east-1 region is hardcoded. Change it.
