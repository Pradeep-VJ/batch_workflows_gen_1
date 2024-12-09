provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "log_bucket" {
  bucket = "restricted-astra-files"
  acl    = "private"
}

resource "aws_emr_cluster" "emr_spark_cluster" {
  name          = "daily_batch_emr_cluster"
  release_label = "emr-6.12.0"
  applications  = ["Hadoop", "Spark"]
  log_uri       = "s3://${aws_s3_bucket.log_bucket.bucket}/logs/"


  ec2_attributes {
    instance_profile = "emr-cluster-role" # IAM instance profile you just created
    subnet_id        = "subnet-02d277817ea4e40d8" # Replace with your subnet ID
  }

  # Master node configuration
  master_instance_group {
    instance_type = "t2.micro"  # Free Tier instance
    instance_count = 1
  }

  # Core node configuration
  core_instance_group {
    instance_type = "t2.micro"  # Free Tier instance
    instance_count = 2
  }

  # Bootstrap action for custom configurations
  bootstrap_action {
    path = "s3://${aws_s3_bucket.log_bucket.bucket}/scripts/emr_bootstrap.sh"
  }

  # Spark environment configuration
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

  # Enable logging to CloudWatch
  enable_debugging = true

  # Optimize cost by auto-terminating the cluster after the job finishes
  auto_terminate = true
}
