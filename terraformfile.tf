provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "log_bucket" {
  bucket = "emr-logs-bucket"
  acl    = "private"
}

resource "aws_emr_cluster" "spark_cluster" {
  name          = "data-processing-cluster"
  release_label = "emr-6.12.0"
  applications  = ["Hadoop", "Spark"]
  log_uri       = "s3://${aws_s3_bucket.log_bucket.bucket}/logs/"

  ec2_attributes {
    instance_profile = aws_iam_instance_profile.emr_profile.arn
    subnet_id        = "subnet-12345678"
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_type = "m5.xlarge"
    instance_count = 2
  }

  bootstrap_action {
    path = "s3://bootstrap-bucket/emr_bootstrap.sh"
  }

  configurations_json = <<EOF
  [
    {
      "Classification": "spark-env",
      "Configurations": [
        {
          "Classification": "export",
          "Properties": {
            "PYSPARK_PYTHON": "/usr/bin/python3"
          }
        }
      ]
    }
  ]
  EOF
}
