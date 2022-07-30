## torianik-music-etl

### Abstract
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)

AWS Glue PySpark ETL pipeline fully managed by terraform. Converst JSON dataset to SQL database hosted on RDS instance.

### Dataset

[Link to Aicrowd chanllenge](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge)

C.W. Chen, P. Lamere, M. Schedl, and H. Zamani. Recsys Challenge 2018: Automatic Music Playlist Continuation. In Proceedings of the 12th ACM Conference on Recommender Systems (RecSys ’18), 2018.

#### Architecture

![torianik music AWS diagram](https://github.com/htorianik/torianik-music-etl/blob/main/doc/torianik-music.drawio.png)

### Deploy

1. Define variables in `.tfvars`:
    * account_id - id of yout AWS account
    * project_name - how you want to call your project (advanced, not supported by the etl)
    * subnet_id - public subnet identitifier
    * secondary_subnet_id - private subnet identifier. Must be in the different AZ then the subnet_id
    * security_group_id - security group that allows inbound postgresql traffic.

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

### Usage

1. Upload JSON slices to a data lake:
```bash
aws s3 cp --recursive local/path/to/dataset/slices/ $( terraform output data_lake )/raw/dataset=mydataset/
```

2. Set up Apache Airflow
   * Start the Airflow.
   * Install requirements from [torianik-music-airflow](https://github.com/htorianik/torianik-music-airflow).
   * Uload dag [torianik-music-airflow](https://github.com/htorianik/torianik-music-airflow).
   * Create PostgreSQL connection using creds from `.tfvars`.
   * Set up AWS connection.

3. Run apache Airflow. Choose option `Trigger DAG w/ config`. Put to the config:
```json
{
    "dataset": "mydataset"
}
```

4. Wait until it's ready. If you did everything correct you should see DAG like this:
![torianik music airflow DAG](https://github.com/htorianik/torianik-music-etl/blob/main/doc/torianik-music-airflow.png)

5. Now you can use filled database. You can get it connection url with:
```bash
terraform output db_conn_url
```


### Development

Run the ETL script locally:
```bash
./dev/run.sh <path to script relative to ./resources/> --dataset=mydatase [--any-other-kwarg]
```

### Additional resources

#### Articles

* [Develop and test AWS Glue locally with docker](https://aws.amazon.com/blogs/big-data/develop-and-test-aws-glue-version-3-0-jobs-locally-using-a-docker-container/)
* [Optimize memory management in AWS Glue](https://aws.amazon.com/blogs/big-data/optimize-memory-management-in-aws-glue/). Used partitions grouping.
* [Comprehensive intro into working with S3 Partitions](https://aws.amazon.com/blogs/big-data/work-with-partitioned-data-in-aws-glue/)

#### Notes

* [Tricky moment about relationalizing](https://stackoverflow.com/questions/69037911/aws-glue-cant-select-fields-after-unnest-or-relationalize)
* Glue does not support overwriting S3 folders. Used `dyf.toDF().write.mode("overwrite")` instead.
