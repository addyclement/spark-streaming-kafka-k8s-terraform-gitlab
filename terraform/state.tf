terraform {
  backend "s3" {
    # Replace this with your bucket name!
    bucket         = "bexley-terraform-state"
    key            = "state/eks-terraform.tfstate"
    region         = "eu-west-2"

    # dynamodb details
    dynamodb_table = "terraform-state"
    encrypt        = true
  }
}
