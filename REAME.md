## torianik-music-etl

### Deploy
1. Create `.tfvars`:
```tfstate
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