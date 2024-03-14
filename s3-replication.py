from aws_cdk import (
    core,
    aws_iam as iam,
    aws_s3 as s3
)

class S3BucketStack(core.Stack):

    def __init__(self,scope:core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)

        self.source_bucket_name_prefix = 'source-s3-bucket-replication-demo-1'
        self.destination_bucket_name_prefix='destination-s3-bucket-replication-demo-1'

        if(self.region == 'us-east-1'):
            self.role=iam.Role(
                self,
                's3_replica_poc_role',
                assumed_by=iam.ServicePrincipal('s3.amazonaws.com'),
                role_name=f's3-replication-role'
            )

            iam.Policy(
                self,
                's3_replica_poc_policy',
                roles=[
                    self.role
                ],
                statements=[
                    self.replication_source_policy(self.get_bucket_arn(self.source_bucket_name_prefix,'us-east-1')),
                    self.replication_policy(self.get_bucket_arn(self.destination_bucket_name_prefix,'us-west-2'))
                ]
            )

            source_bucket = s3.Bucket(
                self,
                'SourceBucket',
                bucket_name=self.source_bucket_name_prefix,
                versioned=True,
                encryption=s3.BucketEncryption.S3_MANAGED
            )

            source_bucket.add_to_resource_policy(
                statement=iam.PolicyStatement(
                    actions=[
                        's3:GetObjectVersionForReplication',
                        's3:GetObjectVersionAcl',
                        's3:GetObjectVersionTagging',
                        's3:GetObjectRetention',
                        's3:GetObjectLegalHold'
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[f'{source_bucket.bucket_arn}/*'],
                    principals=[iam.ServicePrincipal('s3.amazonaws.com')]
                )
            )

            source_bucket.add_replication_configuration(
                rule=s3.ReplicationRule(
                    destination=s3.ReplicationDestination(bucket=s3.Bucket.from_bucket_arn(self, 'DestinationBucket', self.get_bucket_arn(self.destination_bucket_name_prefix,'us-west-2'))),
                    prefix='testing/'
                )
            )

        elif(self.region == 'us-west-2'):
            s3.Bucket(
                self,
                'DestinationBucket',
                bucket_name=self.destination_bucket_name_prefix,
                versioned=True,
                encryption=s3.BucketEncryption.S3_MANAGED
            )
