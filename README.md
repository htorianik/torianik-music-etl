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